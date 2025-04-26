## Rewards.py
Gets the rewards of latest X blocks starting from the highest Y block, thanks to http://payload.de

### Requirements
- pip install python-dotenv requests

Create a `.env` file with the following content:

```dotenv
NUM_CALLS=100
START_BLOCK=22347396
```

How to Run:
```bash
python rewards.py
```

## Charts.py 
Generates charts inside `/charts` folder, using the data from `rewards.py`.

### Requirements
- pip install pandas numpy matplotlib seaborn python-dotenv

Create a `.env` file with the following content:

```dotenv
VALIDATORS_MY_POOL=1350
```
Replace 1350 with the number of validators your pool manages.

## Usage

```bash
python charts.py
```






