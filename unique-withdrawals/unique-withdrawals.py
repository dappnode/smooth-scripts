import requests
import csv
import json

# URL to fetch data
url = 'https://sp-api.dappnode.io/memory/validators'
csv_file_path = 'withdrawal_addresses_with_counts.csv'

def fetch_data(url):
    """Fetch data from a URL and return the JSON data."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def count_addresses(data):
    """Count the occurrences of each withdrawal address with active status."""
    address_counts = {}
    for entry in data:
        status = entry['status']
        if status == 'notsubscribed' or status == 'banned':
            continue  # Skip elements with 'notsubscribed' or 'banned' status
        address = entry['withdrawal_address']
        if address in address_counts:
            address_counts[address] += 1
        else:
            address_counts[address] = 1
    return address_counts

def write_to_csv(address_counts, file_path):
    """Write the addresses and their counts to a CSV file."""
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Withdrawal Address', 'Number of Validators'])
        for address, count in address_counts.items():
            writer.writerow([address, count])

def main():
    # Fetch data from the URL
    data = fetch_data(url)

    if data is not None:
        # Count occurrences of each withdrawal address with active status
        address_counts = count_addresses(data)

        # Write addresses and their counts to CSV file
        write_to_csv(address_counts, csv_file_path)
        print(f"Withdrawal addresses and their validator counts (excluding 'notsubscribed' and 'banned' statuses) have been written to {csv_file_path}")
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    main()
