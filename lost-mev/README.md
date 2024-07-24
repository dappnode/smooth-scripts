### Block Difference Calculation
This script calculates the sum of lost MEV from vanilla (or all) blocks proposed to Smooth. 
- Blocks to be considered are fetched from the oracle, at `https://sp-api.dappnode.io/memory/proposedblocks` endpoint.
- Lost MEV for each block is fetched from payload.de api.

#### Usage

```bash
python3 smooth-lost-mev.py
```
to calculate lost mev from only blocks defined as "vanilla" by the oracle, or
```bash
python3 smooth-lost-mev.py --track-all
```
to calculate lost mev from all blocks (mev and vanilla).
