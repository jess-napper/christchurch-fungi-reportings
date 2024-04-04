import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
df = pd.read_csv("inaturalist_observations_five_years.csv")

# Print the first few rows of the DataFrame
print("First 5 rows of the DataFrame:")
print(df.head(5))

# Get summary statistics of the DataFrame
print("\nSummary statistics:")
print(df.describe())

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())

# Count the number of observations by species
species_counts = df["species_guess"].value_counts()
print("\nObservations by species:")
print(species_counts)

# Visualize the species distribution
plt.figure(figsize=(10, 6))
species_counts.plot(kind="bar")
plt.xlabel("Species")
plt.ylabel("Number of Observations")
plt.title("Species Distribution")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Analyze the observation dates
df["observed_on"] = pd.to_datetime(df["observed_on"])
print("\nObservation date range:")
print(f"Start date: {df['observed_on'].min()}")
print(f"End date: {df['observed_on'].max()}")

# Count observations by date
observations_by_date = df.groupby(df["observed_on"].dt.date).size()
print("\nObservations by date:")
print(observations_by_date)

# Visualize observations over time
plt.figure(figsize=(10, 6))
observations_by_date.plot(kind="line")
plt.xlabel("Date")
plt.ylabel("Number of Observations")
plt.title("Observations Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()