### Wrong Fee Recipient Check

This script checks the Fee Recipient address of all validators subscribed to Smooth. Validator data is fetched from `https://sp-api.dappnode.io/memory/validators` API endpoint. For each validator, `https://sp-api.dappnode.io/registeredrelays/{pubkey}` is called. If not a single relay where the Fee Recipient for that validator is Smooth's is found, the validator is marked as a validator with an incorrect Fee Recipient.

In order to avoid rate limiting, the script sleeps for 3 seconds after each request. Expect this script to take a few minutes to run.

Results are stored in a new `sp_api_logs.log` file, that is created in the same directory as the script and updated while the script advances.

#### Usage

```bash
python3 counting_worng_fees.py
```
