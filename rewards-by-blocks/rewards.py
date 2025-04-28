import os
import csv
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read the number of calls from .env
NUM_CALLS = int(os.getenv("NUM_CALLS", 10))  # default to 10 if not set

# Default starting block if no file exists
DEFAULT_START_BLOCK = int(os.getenv("START_BLOCK", 22347396))

# Output CSV filename
OUTPUT_CSV = "block_data.csv"

# Determine starting block
if os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, mode='r', newline='') as csvfile:
        reader = list(csv.reader(csvfile))
        if len(reader) > 1:
            last_row = reader[-1]
            last_block = int(last_row[2])  # block is third column (index 2)
            start_block = last_block - 1
        else:
            start_block = DEFAULT_START_BLOCK
else:
    start_block = DEFAULT_START_BLOCK

# Determine file mode (append if file exists, else write new)
file_mode = 'a' if os.path.exists(OUTPUT_CSV) else 'w'

# Open the CSV
with open(OUTPUT_CSV, mode=file_mode, newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # If new file, write headers
    if file_mode == 'w':
        writer.writerow(["payment", "slot", "block", "tx_count", "gas_used"])

    # Loop over the number of calls
    for i in range(NUM_CALLS):
        block_number = start_block - i
        url = f"https://api.payload.de/block_info?block={block_number}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extract required fields
            payment = data.get("payment", 0)
            slot = data.get("slot", 0)
            block = data.get("block", 0)
            tx_count = data.get("tx_count", 0)
            gas_used = data.get("gas_used", 0)

            # Write the row to CSV
            writer.writerow([payment, slot, block, tx_count, gas_used])

            print(f"Fetched and saved block {block_number}")

        except Exception as e:
            print(f"Error fetching block {block_number}: {e}")
