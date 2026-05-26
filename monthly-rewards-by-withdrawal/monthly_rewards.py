#!/usr/bin/env python3
import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone


MAINNET_GENESIS_UNIX = 1606824023
DEFAULT_API_URL = "https://sp-api.dappnode.io/"
SECONDS_PER_SLOT = 12
WEI_PER_ETH = 10**18

OUTPUT_COLUMNS = [
    "month",
    "checkpoint_slot",
    "accumulated_rewards_wei",
    "pending_rewards_wei",
    "total_rewards_wei",
    "accumulated_gained_this_month_wei",
    "pending_change_this_month_wei",
    "total_position_change_this_month_wei",
    "accumulated_rewards_eth",
    "pending_rewards_eth",
    "total_rewards_eth",
    "accumulated_gained_this_month_eth",
    "pending_change_this_month_eth",
    "total_position_change_this_month_eth",
]


def output_columns(include_withdrawal_address):
    if include_withdrawal_address:
        return ["withdrawal_address", *OUTPUT_COLUMNS]
    return OUTPUT_COLUMNS


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Calculate monthly oracle rewards by Ethereum withdrawal address."
        )
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=(
            "Oracle API base URL. "
            f"Defaults to {DEFAULT_API_URL}; for example http://localhost:7300"
        ),
    )
    source.add_argument(
        "--state-file",
        help="Path to a previously saved /state JSON response",
    )
    parser.add_argument(
        "--withdrawal-address",
        help=(
            "Withdrawal address to match, case-insensitive. "
            "If omitted, output one monthly series per withdrawal address."
        ),
    )
    parser.add_argument(
        "--genesis-unix",
        type=int,
        default=MAINNET_GENESIS_UNIX,
        help=f"Ethereum genesis unix timestamp. Defaults to mainnet: {MAINNET_GENESIS_UNIX}",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="HTTP timeout in seconds when using --api-url",
    )
    parser.add_argument(
        "--format",
        choices=("table", "csv", "json"),
        default="table",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        help="Write output to this file instead of stdout",
    )
    parser.add_argument(
        "--include-zero-months",
        action="store_true",
        help=(
            "In single-address mode, include months whose last checkpoint has "
            "zero matching validators"
        ),
    )
    return parser.parse_args()


def load_state(args):
    if args.state_file:
        with open(args.state_file, "r", encoding="utf-8") as state_file:
            return json.load(state_file)

    api_url = args.api_url.rstrip("/")
    with urllib.request.urlopen(f"{api_url}/state", timeout=args.timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_committed_states(payload):
    for container in candidate_state_containers(payload):
        if "commited_states" in container:
            return container["commited_states"]
        if "committed_states" in container:
            return container["committed_states"]

    raise KeyError("Could not find 'commited_states' in the /state response")


def candidate_state_containers(payload):
    if isinstance(payload, dict):
        yield payload
        for key in ("state", "State", "data", "Data"):
            nested = payload.get(key)
            if isinstance(nested, dict):
                yield nested


def normalize_committed_states(committed_states):
    if isinstance(committed_states, list):
        for checkpoint in committed_states:
            if isinstance(checkpoint, dict):
                yield checkpoint
        return

    if isinstance(committed_states, dict):
        for slot_key, checkpoint in committed_states.items():
            if not isinstance(checkpoint, dict):
                continue
            if "slot" in checkpoint:
                yield checkpoint
                continue

            checkpoint_with_slot = dict(checkpoint)
            checkpoint_with_slot["slot"] = slot_key
            yield checkpoint_with_slot
        return

    raise TypeError("'commited_states' must be a list or object")


def normalize_validators(validators):
    if isinstance(validators, list):
        for validator in validators:
            if isinstance(validator, dict):
                yield validator
        return

    if isinstance(validators, dict):
        for validator in validators.values():
            if isinstance(validator, dict):
                yield validator


def normalize_address(address):
    return str(address).strip().lower()


def parse_int(value, field_name):
    if value is None:
        return 0
    try:
        return int(str(value), 10)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {field_name}: {value!r}") from exc


def slot_to_month(slot, genesis_unix):
    timestamp = genesis_unix + (slot * SECONDS_PER_SLOT)
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m")


def checkpoint_snapshot(checkpoint, requested_address):
    validators = checkpoint.get("validators", {})
    accumulated = 0
    pending = 0
    matched_validators = 0

    for validator in normalize_validators(validators):
        withdrawal_address = normalize_address(validator.get("withdrawal_address", ""))
        if withdrawal_address != requested_address:
            continue

        matched_validators += 1
        accumulated += parse_int(
            validator.get("accumulated_rewards_wei"),
            "accumulated_rewards_wei",
        )
        pending += parse_int(
            validator.get("pending_rewards_wei"),
            "pending_rewards_wei",
        )

    return {
        "slot": parse_int(checkpoint.get("slot"), "slot"),
        "matched_validators": matched_validators,
        "accumulated_rewards_wei": accumulated,
        "pending_rewards_wei": pending,
        "total_rewards_wei": accumulated + pending,
    }


def checkpoint_snapshots_by_address(checkpoint):
    snapshots = {}
    slot = parse_int(checkpoint.get("slot"), "slot")

    for validator in normalize_validators(checkpoint.get("validators", {})):
        withdrawal_address = normalize_address(validator.get("withdrawal_address", ""))
        if not withdrawal_address:
            continue

        snapshot = snapshots.setdefault(
            withdrawal_address,
            {
                "withdrawal_address": withdrawal_address,
                "slot": slot,
                "matched_validators": 0,
                "accumulated_rewards_wei": 0,
                "pending_rewards_wei": 0,
                "total_rewards_wei": 0,
            },
        )
        accumulated = parse_int(
            validator.get("accumulated_rewards_wei"),
            "accumulated_rewards_wei",
        )
        pending = parse_int(
            validator.get("pending_rewards_wei"),
            "pending_rewards_wei",
        )

        snapshot["matched_validators"] += 1
        snapshot["accumulated_rewards_wei"] += accumulated
        snapshot["pending_rewards_wei"] += pending
        snapshot["total_rewards_wei"] += accumulated + pending

    return snapshots.values()


def monthly_snapshots(
    committed_states,
    requested_address,
    genesis_unix,
    include_zero_months,
):
    snapshots_by_month = {}
    snapshots_by_address_month = {}

    checkpoints = sorted(
        normalize_committed_states(committed_states),
        key=lambda checkpoint: parse_int(checkpoint.get("slot"), "slot"),
    )

    for checkpoint in checkpoints:
        slot = parse_int(checkpoint.get("slot"), "slot")
        month = slot_to_month(slot, genesis_unix)

        if requested_address:
            snapshot = checkpoint_snapshot(checkpoint, requested_address)
            snapshot["month"] = month
            snapshots_by_month[month] = snapshot
            continue

        for snapshot in checkpoint_snapshots_by_address(checkpoint):
            snapshot["month"] = month
            key = (snapshot["withdrawal_address"], month)
            snapshots_by_address_month[key] = snapshot

    if not requested_address:
        return [
            snapshot
            for _, snapshot in sorted(
                snapshots_by_address_month.items(),
                key=lambda item: (item[0][0], item[0][1]),
            )
        ]

    rows = [snapshots_by_month[month] for month in sorted(snapshots_by_month)]
    if include_zero_months:
        return rows

    return [snapshot for snapshot in rows if snapshot["matched_validators"] > 0]


def add_deltas(monthly_rows, include_withdrawal_address):
    previous_by_address = {}
    previous_single = None
    rows = []

    for snapshot in monthly_rows:
        previous_key = (
            snapshot.get("withdrawal_address")
            if include_withdrawal_address
            else None
        )
        previous = (
            previous_by_address.get(previous_key)
            if include_withdrawal_address
            else previous_single
        )
        if previous is None:
            previous = {
                "accumulated_rewards_wei": 0,
                "pending_rewards_wei": 0,
                "total_rewards_wei": 0,
            }

        row = {}
        if include_withdrawal_address:
            row["withdrawal_address"] = snapshot["withdrawal_address"]

        row.update(
            {
                "month": snapshot["month"],
                "checkpoint_slot": snapshot["slot"],
                "accumulated_rewards_wei": snapshot["accumulated_rewards_wei"],
                "pending_rewards_wei": snapshot["pending_rewards_wei"],
                "total_rewards_wei": snapshot["total_rewards_wei"],
                "accumulated_gained_this_month_wei": (
                    snapshot["accumulated_rewards_wei"]
                    - previous["accumulated_rewards_wei"]
                ),
                "pending_change_this_month_wei": (
                    snapshot["pending_rewards_wei"] - previous["pending_rewards_wei"]
                ),
                "total_position_change_this_month_wei": (
                    snapshot["total_rewards_wei"] - previous["total_rewards_wei"]
                ),
            }
        )
        add_eth_columns(row)
        rows.append(row)

        if include_withdrawal_address:
            previous_by_address[previous_key] = snapshot
        else:
            previous_single = snapshot

    return rows


def add_eth_columns(row):
    wei_to_eth_columns = {
        "accumulated_rewards_wei": "accumulated_rewards_eth",
        "pending_rewards_wei": "pending_rewards_eth",
        "total_rewards_wei": "total_rewards_eth",
        "accumulated_gained_this_month_wei": "accumulated_gained_this_month_eth",
        "pending_change_this_month_wei": "pending_change_this_month_eth",
        "total_position_change_this_month_wei": "total_position_change_this_month_eth",
    }
    for wei_column, eth_column in wei_to_eth_columns.items():
        row[eth_column] = wei_to_eth(row[wei_column])


def wei_to_eth(wei):
    sign = "-" if wei < 0 else ""
    wei_abs = abs(wei)
    whole, fractional = divmod(wei_abs, WEI_PER_ETH)
    return f"{sign}{whole}.{fractional:018d}"


def write_output(rows, output_format, output_path, columns):
    output_file = (
        open(output_path, "w", newline="", encoding="utf-8")
        if output_path
        else sys.stdout
    )
    try:
        if output_format == "json":
            json.dump(rows, output_file, indent=2)
            output_file.write("\n")
        elif output_format == "csv":
            writer = csv.DictWriter(output_file, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        else:
            output_file.write(format_table(rows, columns))
            output_file.write("\n")
    finally:
        if output_path:
            output_file.close()


def format_table(rows, columns):
    if not rows:
        return "No matching monthly checkpoints found."

    string_rows = [
        {column: str(row[column]) for column in columns}
        for row in rows
    ]
    widths = {
        column: max(len(column), *(len(row[column]) for row in string_rows))
        for column in columns
    }

    header = " | ".join(column.ljust(widths[column]) for column in columns)
    separator = "-+-".join("-" * widths[column] for column in columns)
    body = [
        " | ".join(row[column].rjust(widths[column]) for column in columns)
        for row in string_rows
    ]
    return "\n".join([header, separator, *body])


def main():
    args = parse_args()
    requested_address = (
        normalize_address(args.withdrawal_address)
        if args.withdrawal_address
        else None
    )
    include_withdrawal_address = requested_address is None

    try:
        state = load_state(args)
        committed_states = extract_committed_states(state)
        snapshots = monthly_snapshots(
            committed_states,
            requested_address,
            args.genesis_unix,
            args.include_zero_months,
        )
        rows = add_deltas(snapshots, include_withdrawal_address)
        write_output(
            rows,
            args.format,
            args.output,
            output_columns(include_withdrawal_address),
        )
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"Failed to fetch /state: {exc}", file=sys.stderr)
        return 1
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to process state: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
