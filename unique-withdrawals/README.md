### Unique withdrawals in Smooth

This Python script fetches data from the `https://sp-api.dappnode.io/memory/validators` API endpoint to analyze and count occurrences of withdrawal addresses based on their status. It focuses on active validators, excluding those marked as 'notsubscribed' or 'banned'.

Results are stored in a new `withdrawal_addresses_with_counts.csv`file.

#### Usage

```bash
python3 unique-withdrawals.py
```