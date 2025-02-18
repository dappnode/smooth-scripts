### Smooth-scripts

Collection of scripts related to Smooth, Dappnode's MEV Smoothing Pool. 

### SmoothDAO

The [results](./acc-by-withdrawal/results) folder is updated every 8 hours with the latest data from the Oracle. It contains a JSON file with the accumulated rewards of each withdrawal address in Smooth. More details in the [README](./acc-by-withdrawal/README.md).

### Dependencies

Ensure Python 3 is installed, as all scripts run with Python 3.x. The following are the required libraries, which can be installed with pip:

```bash
pip install requests
pip install web3
pip install python-dotenv
```

The rest of the libraries used (csv, json, concurrent.futures, statistics, logging, time, and os) are included with the standard Python library and do not require separate installation.