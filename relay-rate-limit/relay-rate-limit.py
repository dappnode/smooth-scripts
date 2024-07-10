import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

# List of API endpoints
endpoints = [
    "https://0xa15b52576bcbf1072f4a011c0f99f9fb6c66f3e1ff321f11f461d15e31b1cb359caa092c71bbded0bae5b5ea401aab7e@aestus.live",
    "https://0xa7ab7a996c8584251c8f925da3170bdfd6ebc75d50f5ddc4050a6fdc77f2a3b5fce2cc750d0865e05d7228af97d69561@agnostic-relay.net",
    "https://0x8b5d2e73e2a3a55c6c87b8b6eb92e0149a125c852751db1422fa951e42a09b82c142c3ea98d0d9930b056a3bc9896b8f@bloxroute.max-profit.blxrbdn.com",
    "https://0xb0b07cd0abef743db4260b0ed50619cf6ad4d82064cb4fbec9d3ec530f7c5e6793d9f286c4e082c0244ffb9f2658fe88@bloxroute.regulated.blxrbdn.com",
    "https://0xb3ee7afcf27f1f1259ac1787876318c6584ee353097a50ed84f51a1f21a323b3736f271a895c7ce918c038e4265918be@relay.edennetwork.io",
    "https://0xac6e77dfe25ecd6110b8e780608cce0dab71fdd5ebea22a16c0205200f2f8e2e3ad3b71d3499c54ad14d6c21b41a37ae@boost-relay.flashbots.net",
    "https://0x98650451ba02064f7b000f5768cf0cf4d4e492317d82871bdc87ef841a0743f69f0f1eea11168503240ac35d101c9135@mainnet-relay.securerpc.com",
    "https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money",
    "https://0x8c7d33605ecef85403f8b7289c8058f440cbb6bf72b055dfe2f3e2c6695b6a1ea5a9cd0eb3a7982927a463feb4c3dae2@relay.wenmerge.com"
]

endpoint_path = "/relay/v1/data/validator_registration"
pubkey = "0xa7396f2b6255f1598aad576ea429515077322461531098878226a949b369b0063fee82adaa5df2ad8f9f7d07c3796be2"

# Function to send a request and return the entire response
def send_request(endpoint):
    url = f"{endpoint}{endpoint_path}?pubkey={pubkey}"
    try:
        response = requests.get(url)
        return response
    except requests.RequestException as e:
        return f"Error: {str(e)}"

# Function to handle requests for each relay
def perform_requests(endpoint):
    print(f"Starting requests for {endpoint}")
    start_time = time.time()
    results = {}
    unique_responses = set()

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(send_request, endpoint) for _ in range(2000)]
        for future in as_completed(futures):
            response = future.result()
            if isinstance(response, requests.Response):
                # Process HTTP responses
                status_code = response.status_code
                results[status_code] = results.get(status_code, 0) + 1
                try:
                    # Attempt to parse JSON response, otherwise log text
                    response_content = response.json()
                except ValueError:
                    response_content = response.text
                unique_responses.add((status_code, json.dumps(response_content, sort_keys=True) if isinstance(response_content, dict) else response_content))
            else:
                # Process non-HTTP responses (errors)
                unique_responses.add(("Error", response))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Finished requests for {endpoint}. Time elapsed: {elapsed_time:.2f} seconds")

    # Writing results to file after each relay
    with open("relay-results-api-2000.txt", "a") as file:
        file.write(f"{endpoint}:\n")
        file.write(f"Elapsed Time: {elapsed_time:.2f} seconds\n")
        for status, count in results.items():
            status_label = f"Status {status}"
            file.write(f"{status_label}: {count} times\n")
        file.write("Unique Responses:\n")
        for status, response in unique_responses:
            file.write(f"Status {status}: {response}\n")
        file.write("\n")

# Iterating over each endpoint
for endpoint in endpoints:
    perform_requests(endpoint)

print("All requests completed. Check relay-results-api.txt for summaries.")