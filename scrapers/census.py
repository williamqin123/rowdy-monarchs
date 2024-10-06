import censusdata
import pandas as pd

# Specify the years you want to retrieve data for
years = range(2000, 2025)  # Example: 2000 to 2020

# Prepare an empty DataFrame to store all data
all_data = pd.DataFrame()

# Loop through each year to get population estimates
for year in years:
    # Retrieve population data for all counties
    data = censusdata.download(
        "pep",
        censusdata.censusgeo([("county", "*"), ("state", "*")]),
        [censusdata.censusvar("sf1", year, "B01003_001E")],
        year=year,
    )

    # Reset the index and add the year column
    data.reset_index(inplace=True)
    data["YEAR"] = year

    # Append to the all_data DataFrame
    all_data = pd.concat([all_data, data], ignore_index=True)

# Rename columns for clarity
all_data.columns = ["STATE", "COUNTY", "POPULATION", "YEAR"]

# Display the DataFrame
print(all_data)

# Optionally, save to CSV
all_data.to_csv("scrapers/CensusBureau/population_estimates_by_county.csv", index=False)
