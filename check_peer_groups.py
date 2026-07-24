import pandas as pd

peer = pd.read_excel(
    "data/raw/supporting_datasets/peer_groups.xlsx"
)

print("Columns:")
print(peer.columns.tolist())

print("\nFirst 5 rows:")
print(peer.head())