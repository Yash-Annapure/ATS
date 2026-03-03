import pandas as pd
import sqlite3
import os

# Define paths to your CSV files
csv_files = {
    'Git_hub': r"../Profile_Data/Github_Profiles.csv",
    'Leet_code': r"../Profile_Data/leetcode_500_profiles.csv",
    'Stack_overflow': r"../Profile_Data/StackOverflow-20K-Basedata (1).csv"
}

# Create a connection to SQLite database
# If the database doesn't exist, it will be created
db_name = 'database.db'
conn = sqlite3.connect(db_name)

print(f"Database '{db_name}' created/connected successfully!")

# Dictionary to store DataFrames
dataframes = {}

# Load each CSV and store in database
for table_name, csv_path in csv_files.items():
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        dataframes[table_name] = df
        
        # Store DataFrame in SQLite database
        # if_exists options: 'fail', 'replace', 'append'
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"Table '{table_name}' created with {len(df)} rows and {len(df.columns)} columns")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found!")
    except Exception as e:
        print(f"Error loading '{csv_path}': {str(e)}")

# Define paths to shortlisted candidates CSV files
shortlisted_files = {
    'top_github': r"../ML/Shortlisted_candidates/github_shortlisted_candidates.csv",
    'top_leetcode': r"../ML/Shortlisted_candidates/leetcode_shortlisted_candidates.csv",
    'top_stackoverflow': r"../ML/Shortlisted_candidates/stackoverflow_shortlisted_candidates.csv"
}

# Load shortlisted candidates into separate tables
for table_name, csv_path in shortlisted_files.items():
    try:
        df = pd.read_csv(csv_path)
        
        # Normalize columns: make all lowercase
        df.columns = df.columns.str.lower()
        
        # Standardize username column for consistency (api usage)
        if 'display_name' in df.columns:
            df.rename(columns={'display_name': 'username'}, inplace=True)
            
        # Ensure we don't have duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]

        # Store in separate tables
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Table '{table_name}' created with {len(df)} rows")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found!")
    except Exception as e:
        print(f"Error loading '{csv_path}': {str(e)}")

print(f"\nAll CSV files loaded into database '{db_name}'")

# Get list of all tables in the database
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\n" + "="*50)
print("TABLES IN DATABASE:")
print("="*50)
for table in tables:
    print(f"  • {table[0]}")

# STEP 5: Query Sample Data
# ============================================
if tables:
    table_to_query = tables[0][0]  # Query first table
    
    print(f"\n{'='*60}")
    print(f"SAMPLE DATA FROM '{table_to_query}' (First 5 rows):")
    print("="*60)
    
    query = f"SELECT * FROM {table_to_query} LIMIT 5"
    sample_data = pd.read_sql_query(query, conn)
    print(sample_data)
    
    # Show column info
    print(f"\n{'='*60}")
    print(f"COLUMN INFORMATION:")
    print("="*60)
    query_info = f"PRAGMA table_info({table_to_query})"
    table_info = pd.read_sql_query(query_info, conn)
    print(table_info[['name', 'type']])

# ============================================
# STEP 6: Close Connection
# ============================================
conn.close()
print(f"\nDatabase connection closed successfully!")


'''
Reading Data from Database Later
python# Connect to existing database
conn = sqlite3.connect('my_database.db')

# Read entire table
df = pd.read_sql_query("SELECT * FROM nyc_airbnb", conn)

# Read with conditions
df_filtered = pd.read_sql_query(
    "SELECT * FROM nyc_airbnb WHERE price > 100", 
    conn
)

# Close connection
conn.close()

-------------------------------------------------------------------------------
Update/Delete Operations
pythonconn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Update data
cursor.execute("UPDATE nyc_airbnb SET price = price * 1.1 WHERE neighbourhood = 'Manhattan'")

# Delete data
cursor.execute("DELETE FROM nyc_airbnb WHERE price = 0")

# Commit changes
conn.commit()
conn.close()

'''