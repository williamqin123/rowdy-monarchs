from matplotlib import pyplot as plt
import sqlite3 as sql
import pandas as pd

# Path to your SQLite database file
database_path = 'your_database.db'

# Connect to the SQLite database
conn = sql.connect(database_path)

# Define your SQL query
query = "SELECT * FROM your_table_name"  # Replace 'your_table_name' with the actual table name

# Read the data into a DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Display the DataFrame
print(df)