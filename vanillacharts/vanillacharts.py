import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Constants
SLOT_DURATION = 12  # seconds
GENESIS_TIMESTAMP = 1606824023  # Slot 0 timestamp

# Fetch data
url = "https://sp-api.dappnode.io/memory/proposedblocks"
response = requests.get(url)
data = response.json()

# Load into DataFrame
df = pd.DataFrame(data)

# Convert slot to UTC datetime
df['timestamp'] = df['slot'].apply(lambda slot: datetime.utcfromtimestamp(GENESIS_TIMESTAMP + slot * SLOT_DURATION))

# Floor to day
df['date'] = df['timestamp'].dt.floor('D')

# Count all blocks per day
total_daily_counts = df.groupby('date').size()

# Count vanilla blocks per day
vanila_daily_counts = df[df['reward_type'] == 'vanila'].groupby('date').size()

# Ensure both series align
daily_df = pd.DataFrame({
    'total_blocks': total_daily_counts,
    'vanila_blocks': vanila_daily_counts
}).fillna(0)

# Calculate percentage of vanilla blocks
daily_df['vanila_pct'] = (daily_df['vanila_blocks'] / daily_df['total_blocks']) * 100

# 10-day rolling average of vanilla percentage
daily_df['vanila_pct_rolling'] = daily_df['vanila_pct'].rolling(window=21).mean()

# Dates of interest
events = {
    "Smooth Terms of Use Approved": datetime(2024, 11, 2, 17, 58),
    "First Operator Banned": datetime(2025, 3, 10, 17, 6),
    "The Purge": datetime(2025, 3, 20, 16, 28)
}

# Plot
plt.figure(figsize=(12, 6))
plt.plot(daily_df['vanila_pct'], label='Daily % of Vanilla Blocks', alpha=0.3)
plt.plot(daily_df['vanila_pct_rolling'], label='10-Day Rolling Avg %', linewidth=2)

# Add vertical lines and labels
for label, date in events.items():
    plt.axvline(x=date, color='red', linestyle='--', alpha=0.7)
    plt.text(date, 57, label, rotation=90, verticalalignment='top', color='red', fontsize=9)

plt.title('Percentage of Vanilla Blocks Over Time (10-Day Rolling Average)')
plt.xlabel('Date')
plt.ylabel('Vanilla Block Percentage (%)')
plt.ylim(0, 60)  # Limit y-axis to 60%
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("vanilla_block_percentage.png", dpi=300)
