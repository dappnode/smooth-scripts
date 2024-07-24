import requests
import time
import csv
from datetime import datetime
import argparse

def get_blocks(track_all=False):
    url = "https://sp-api.dappnode.io/memory/proposedblocks"
    try:
        response = requests.get(url)
        response.raise_for_status()
        blocks = response.json()
        if track_all:
            return [block['block'] for block in blocks]
        else:
            return [block['block'] for block in blocks if block['reward_type'] == 'vanila']
    except requests.RequestException as e:
        print(f"Failed to fetch data: {e}")
        return []

def get_block_difference(block_number):
    url = f"https://api.payload.de/block_info?block={block_number}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        block_info = response.json()
        return float(block_info['difference'])
    except requests.RequestException as e:
        print(f"Failed to fetch block {block_number}: {e}")
        return None

def write_to_csv(block_number, difference, timestamp):
    with open('results.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, block_number, difference])

def write_summary_to_file(total_difference, top_differences):
    with open('stats_summary.txt', 'w') as file:
        file.write(f"Total Difference Sum: {total_difference}\n")
        file.write("Top 10 Block Differences:\n")
        for diff, block in top_differences:
            file.write(f"Block {block}: {diff}\n")

def main(track_all):
    # Check if the file exists, if not create and write the header
    try:
        with open('results.csv', 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Block Number", "Difference"])
    except FileExistsError:
        pass

    blocks = get_blocks(track_all)
    total_difference = 0.0
    differences = []

    for block in blocks:
        difference = get_block_difference(block)
        if difference is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_to_csv(block, difference, timestamp)
            total_difference += difference
            differences.append((difference, block))
        time.sleep(1)  # Adjust rate limiting as necessary

    # Sorting to find top 10 differences
    differences.sort(reverse=True, key=lambda x: x[0])
    top_differences = differences[:10]

    # Write summary stats to file
    write_summary_to_file(total_difference, top_differences)

    # Print the same information to the console
    print(f"Total Difference Sum: {total_difference}")
    print("Top 10 Block Differences:")
    for diff, block in top_differences:
        print(f"Block {block}: {diff}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Track Ethereum block differences.')
    parser.add_argument('--track-all', action='store_true', help='Track all blocks instead of only those with reward_type == "vanila"')
    args = parser.parse_args()
    main(args.track_all)
