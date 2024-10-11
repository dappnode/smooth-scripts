### Validator Status and Pending Rewards Analysis

This script fetches all validator information from oracle's `https://sp-api.dappnode.io/memory/validators` API endpoint. It retrieves the status and pending rewards for each validator and subsequently calls the `eth/v1/beacon/states/finalized/validators` beacon API endpoint with the validator indices to obtain the most recent statuses.

The script aggregates the following information:

- The count of validators in each status category (e.g., "pending_initialized", "active_ongoing", etc.).
- A detailed list of validators that are not in the "active_ongoing" status, including their index, pending rewards (in Wei), and current status.
- The count and total sum of pending rewards (in Wei) for validators that are not "active_ongoing" and have non-zero pending rewards.
- The validator with the highest pending rewards among those that are not "active_ongoing", including its index, status, and pending rewards amount.
- The results are saved in a file named validator_results.txt (same directory).

## Usage

Run the script using Python:

```bash
python3 validator-status-analysis.py
```

Make sure the script has internet access and the required endpoints are available for it to function correctly.