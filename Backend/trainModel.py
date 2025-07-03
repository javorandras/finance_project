import pandas as pd
from app.utils import clean_description
from app.categorizer import Categorizer

# Load labeled transaction data
df = pd.read_csv("data/sample_transactions.csv")
df["clean_description"] = df["Description"].apply(clean_description)

# Train model
categorizer = Categorizer()
categorizer.train(df["clean_description"], df["Category"])

# Save model
categorizer.save()
print("Model trained and saved.")
