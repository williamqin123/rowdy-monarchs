from matplotlib import pyplot as plt
import sqlite3 as sql
import pandas as pd, numpy as np


def readSQL(suffix: str):
    # Path to your SQLite database file
    database_path = f"scrapers/JourneyNorth/journeynorth_{suffix}.db"
    # Connect to the SQLite database
    conn = sql.connect(database_path)
    # Define your SQL query
    query = "SELECT * FROM sightings"
    # Read the data into a DataFrame
    df = pd.read_sql_query(query, conn)
    # Close the database connection
    conn.close()
    # Display the DataFrame
    # print(df)

    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    df["year"] = df["date"].map(lambda x: x.year)

    q = df["qty"].quantile(0.999)  # top 0.1% of entered quatities = possible trolls
    df_no_outliers = df[df["qty"] < q]  # excludes top 0.1% of entered quantities]

    return df_no_outliers


suffixes = ["milkweed", "egg", "larva", "adult", "other"]
tables = [readSQL(s) for s in suffixes]
tables_labeled = dict(zip(suffixes, tables))

xr = np.arange(1996, 2025)
for k, df in tables_labeled.items():
    series = []
    for y in xr:
        filtered_this_year = df[df["year"] == y]
        series.append(filtered_this_year["qty"].sum())

    plt.plot(xr, series, label=k)

plt.legend()

plt.savefig("vis/exports/categories_lines.png")

plt.show()

#

agg = [df.groupby([df["year"]])["qty"].sum().reset_index() for df in tables]

plt.stackplot(
    xr,
    *[
        np.array([agg[i][agg[i]["year"] == y]["qty"].sum() for y in range(1996, 2025)])
        for i, s in enumerate(suffixes)
    ],
    labels=suffixes,
)

plt.legend()

plt.savefig("vis/exports/categories_stack.png")

plt.show()

plt.stackplot(
    xr,
    *[
        np.array(
            [
                100
                * agg[i][agg[i]["year"] == y]["qty"].sum()
                / sum(
                    [
                        agg[i_][agg[i_]["year"] == y]["qty"].sum()
                        for i_ in range(len(suffixes))
                    ]
                )
                for y in range(1996, 2025)
            ]
        )
        for i, s in enumerate(suffixes)
    ],
    labels=suffixes,
)


plt.legend()

plt.savefig("vis/exports/categories_stack_100%.png")

plt.show()
