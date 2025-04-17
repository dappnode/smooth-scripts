import requests

# Base URL for the beacon chain API
BEACON_CHAIN_URL = "http://beacon-chain.prysm-holesky.dappnode:3500"

# URL for fetching validators from the memory API
MEMORY_VALIDATORS_URL = "https://sp-api.dappnode.io/memory/validators"

def get_validators():
    try:
        # Fetching data from the memory validators endpoint
        response = requests.get(MEMORY_VALIDATORS_URL)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the response JSON
        validators = response.json()

        # Extract all validator indices
        validator_indices = [validator['validator_index'] for validator in validators]

        print(f"Found {len(validator_indices)} validators.")

        return validator_indices

    except requests.RequestException as e:
        print(f"Error fetching validators: {e}")
        return []

def fetch_validators_by_index(indices):
    try:
        # Make a call for validators based on their indices
        state = "head"  # You can modify this state as per your requirement
        indices_str = ",".join(map(str, indices))
        url = f"{BEACON_CHAIN_URL}/eth/v1/beacon/states/{state}/validators?id={indices_str}"

        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        # Parse and return the response JSON
        data = response.json()
        return data

    except requests.RequestException as e:
        print(f"Error fetching validators by index: {e}")
        return {}

def main():
    # Get all validator indices
    validator_indices = get_validators()

    if validator_indices:
        # Fetch validators based on the retrieved indices
        validators_data = fetch_validators_by_index(validator_indices)

        if validators_data:
            print("Validators data fetched successfully.")
            print(validators_data)
        else:
            print("No validators data returned.")
    else:
        print("No validators found.")

if __name__ == "__main__":
    main()
