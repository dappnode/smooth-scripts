### Validator Block Rewards

This script fetches all blocks successfully proposed to the pool through `https://sp-api.dappnode.io/memory/proposedblocks` API endpoint. It only considers blocks proposed by validators which index is one of `INDEX` env variable, and its slot is between `START_SLOT` and `END_SLOT`. A `REVERSE` env variable can be set to `true` if we want to consider ALL blocks of the pool between those slots BUT the ones proposed by validators which index is one of `INDEX`.

The script outputs a CSV file named `rewards.csv` that contains columns for slot, validator index, and the reward in Ether. It also prints the median and average rewards, along with other relevant statistics, to the console.

## Usage

A `.env` file is required to set the following environment variables: `INDEX`, `START_SLOT`, `END_SLOT`, and `REVERSE`. Example in the `.env.example` file.

```bash
python3 validator-rewards.py
```