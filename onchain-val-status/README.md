### Beacon Status & Withdrawal Address Analysis

This script queries validator data from the oracle’s https://sp-api.dappnode.io/memory/validators API endpoint. It analyzes the beacon statuses of all validators that have ever been subscribed to the oracle and extracts the most frequent withdrawal addresses for those that have completed the withdrawal process.

The script aggregates the following information:

- A count of validators in each unique beacon_status category (e.g., "active_ongoing", "pending_initialized", "withdrawal_done", etc.).
- The top 10 most common withdrawal addresses among validators whose beacon_status is "withdrawal_done", along with how many validators each address corresponds to.
- All results are saved in a file named results.txt in the same directory.

## Usage

Run the script using Python:

```bash
python3 beacon-status-summary.py
