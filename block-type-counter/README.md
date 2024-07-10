### Block Type Counter

This script fetches all blocks successfully proposed to the pool through `https://sp-api.dappnode.io/memory/proposedblocks` API endpoint. When executed, it prints to the console the number of blocks proposed by each block type, aswell as all vanilla blocks sorted by ETH reward. These are also saved in a `vanilla-blocks.csv` file.

#### Usage

```bash
python3 block-counter.py
```