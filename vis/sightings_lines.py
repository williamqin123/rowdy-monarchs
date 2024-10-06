from matplotlib import pyplot as plt
import sqlite3 as sql
import pandas as pd, numpy as np

# Path to your SQLite database file
database_path = "scrapers/JourneyNorth/journeynorth_adult.db"

# Connect to the SQLite database
conn = sql.connect(database_path)

# Define your SQL query
query = "SELECT * FROM sightings"

# Read the data into a DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Display the DataFrame
print(df)

df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")

q = df["qty"].quantile(0.999)  # top 0.1% of entered quatities = possible trolls
df_no_outliers = df[df["qty"] < q]  # excludes top 0.1% of entered quantities]

months_strs = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

xr = np.arange(1996, 2025)
for m in range(12):
    series = []
    for y in xr:
        filtered_this_month = df_no_outliers[
            (df_no_outliers["date"].dt.month == m)
            & (df_no_outliers["date"].dt.year == y)
        ]
        series.append(filtered_this_month["qty"].sum())

    plt.plot(xr, series, label=months_strs[m])

plt.legend()

plt.savefig("vis/exports/sightings_lines.png")

plt.show()

#

agg = df_no_outliers.groupby(
    [df_no_outliers["date"].dt.month, df_no_outliers["date"].dt.year]
)["qty"].sum()
agg.index.names = ["month", "year"]
agg = agg.reset_index()
plt.stackplot(
    xr,
    *[
        np.array(
            [
                (tmp := agg[agg["month"] == m].sort_values("year"))[tmp["year"] == y][
                    "qty"
                ].sum()
                for y in range(1996, 2025)
            ]
        )
        for m in range(12)
    ],
    labels=months_strs,
)

plt.legend()

plt.savefig("vis/exports/sightings_stack.png")

plt.show()

plt.stackplot(
    xr,
    *[
        np.array(
            [
                100
                * (tmp := agg[agg["month"] == m].sort_values("year"))[tmp["year"] == y][
                    "qty"
                ].sum()
                / agg[agg["year"] == y]["qty"].sum()
                for y in range(1996, 2025)
            ]
        )
        for m in range(12)
    ],
    labels=months_strs,
)

plt.legend()

plt.savefig("vis/exports/sightings_stack_100%.png")

plt.show()
