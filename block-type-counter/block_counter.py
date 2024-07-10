import requests
import csv

# URL from which to fetch data
url = "https://sp-api.dappnode.io/memory/proposedblocks"

# Sending a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parsing the JSON data
    data = response.json()

    # Counters for the reward types and list for vanilla entries
    mev_count = 0
    vanilla_entries = []

    # Iterate through each entry and process reward types
    for entry in data:
        if entry.get('reward_type') == 'mev':
            mev_count += 1
        elif entry.get('reward_type') == 'vanila':
            # Convert reward_wei to ether and add to the list
            reward_ether = int(entry['reward_wei']) / 10**18
            entry['reward_ether'] = reward_ether
            vanilla_entries.append(entry)

    # Sorting vanilla entries by reward amount in ether in descending order
    vanilla_entries_sorted = sorted(vanilla_entries, key=lambda x: x['reward_ether'], reverse=True)

    # Writing data to a CSV file
    with open('vanilla-blocks.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Writing headers
        writer.writerow(['Block', 'Reward (ETH)'])
        # Writing data
        for entry in vanilla_entries_sorted:
            writer.writerow([entry['block'], entry['reward_ether']])

    # Output the results
    print(f"Number of entries with reward_type 'mev': {mev_count}")
    print(f"Number of entries with reward_type 'vanilla': {len(vanilla_entries)}")
    print("Vanilla entries sorted by reward amount in ether:")
    for entry in vanilla_entries_sorted:
        print(f"Block: {entry['block']}, Reward: {entry['reward_ether']} ETH")
else:
    print("Failed to retrieve data")
