# Monthly rewards by withdrawal address

Fetches the oracle `/state` endpoint and builds a month-by-month reward table for
validators grouped by withdrawal address.

By default, it outputs all withdrawal addresses:

```bash
python3 monthly-rewards-by-withdrawal/monthly_rewards.py
```

To filter to one withdrawal address:

```bash
python3 monthly-rewards-by-withdrawal/monthly_rewards.py \
  --withdrawal-address 0xabc... \
  --genesis-unix 1606824023
```

The default API URL is `https://sp-api.dappnode.io/` and mainnet genesis
(`1606824023`) is also the default, so both can be omitted for mainnet:

```bash
python3 monthly-rewards-by-withdrawal/monthly_rewards.py \
  --withdrawal-address 0xabc...
```

Use `--api-url` for a local or custom oracle:

```bash
python3 monthly-rewards-by-withdrawal/monthly_rewards.py \
  --api-url http://localhost:7300 \
  --withdrawal-address 0xabc...
```

The script uses Python integers for wei arithmetic. It keeps the last checkpoint
snapshot for each UTC calendar month, then calculates deltas against the previous
monthly snapshot for the same withdrawal address. The first emitted month is
compared against zero. In single-address mode, months whose last checkpoint has
no matching validators are skipped by default; add `--include-zero-months` to
keep them.

CSV output:

```bash
python3 monthly-rewards-by-withdrawal/monthly_rewards.py \
  --format csv \
  --output monthly_rewards.csv
```

If `/state` is not reachable or is too large to fetch repeatedly, save the JSON
once and run from disk:

```bash
curl http://localhost:7300/state > state.json

python3 monthly-rewards-by-withdrawal/monthly_rewards.py \
  --state-file state.json
```
