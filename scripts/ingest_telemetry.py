"""
scripts/ingest_telemetry.py
Parses the raw CSV dataset and populates the legacy TBL_SC_FLEET_HIST_RAW table in MSSQL.
"""
from pathlib import Path
import pandas as pd
import urllib
import os
import random
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Set paths based on scripts/ directory
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

load_dotenv(project_root / ".env")

# Adjust path to match your actual CSV location
data_path = project_root / "data" / "raw" / "dynamic_supply_chain_logistics_dataset.csv"

# 1. Map to the .env variable names specified in CLAUDE.md
db_host = os.getenv("MSSQL_HOST", "localhost")
db_port = os.getenv("MSSQL_PORT", "1433")
# Must use the SA admin user for ingestion (creating/replacing tables), NOT the restricted agent user
db_user = "sa" 
db_password = os.getenv("MSSQL_PASSWORD")
db_name = os.getenv("MSSQL_DATABASE", "ColdChainDB")

if not data_path.exists():
    print(f"Error: CSV file not found at {data_path}")
    print("Please place the dataset there and run again.")
    exit(1)

print(f"Loading CSV from {data_path}...")
df = pd.read_csv(data_path)

# 2. Map columns to match the dbo.TBL_SC_FLEET_HIST_RAW schema expected by VW_ACTIVE_FLEET
# Expected by the view: vehicle ID, driver name, current temp, target temp range, GPS, speed, fuel
legacy_mapping = {
    'Vehicle_ID': 'VehicleID',          # Assuming CSV has this, else we'll fallback below
    'Driver_Name': 'DriverName',
    'vehicle_gps_latitude': 'Latitude',
    'vehicle_gps_longitude': 'Longitude',
    'iot_temperature': 'CargoTempC',
    'cargo_condition_status': 'Status',
    'Speed_kmh': 'Speed',
    'Fuel_Level_pct': 'FuelLevel'
}

# Create a new DataFrame mapping the known columns
mapped_cols = {}
for old_col, new_col in legacy_mapping.items():
    if old_col in df.columns:
        mapped_cols[new_col] = df[old_col]
    else:
        # Fill missing expected columns with synthetic data for demonstration
        if new_col == 'VehicleID':
            mapped_cols[new_col] = [f"TRK-{i:04d}" for i in range(1, len(df) + 1)]
        elif new_col == 'DriverName':
            mapped_cols[new_col] = [f"Driver_{i}" for i in range(1, len(df) + 1)]
        elif new_col == 'Speed':
            mapped_cols[new_col] = [random.randint(40, 90) for _ in range(len(df))]
        elif new_col == 'FuelLevel':
            mapped_cols[new_col] = [random.randint(10, 100) for _ in range(len(df))]
        elif new_col == 'Latitude':
            mapped_cols[new_col] = [40.7128 + random.uniform(-1, 1) for _ in range(len(df))]
        elif new_col == 'Longitude':
            mapped_cols[new_col] = [-74.0060 + random.uniform(-1, 1) for _ in range(len(df))]
        elif new_col == 'CargoTempC':
            mapped_cols[new_col] = [random.uniform(-25.0, 5.0) for _ in range(len(df))]
        elif new_col == 'Status':
            mapped_cols[new_col] = ["Normal" for _ in range(len(df))]

df_legacy = pd.DataFrame(mapped_cols)

# Add Target Temperature Range required by the view
df_legacy['TargetTempRange'] = "-20°C to -10°C"

# Generate a sequential FleetID for the primary key if it doesn't exist in the CSV
df_legacy.insert(0, 'FleetID', range(1, 1 + len(df_legacy)))

# Ensure LastUpdated is set
df_legacy['LastUpdated'] = pd.Timestamp.now()

# 3. Connect to MSSQL using SQLAlchemy and pyodbc
print(f"Connecting to MSSQL Database: {db_name}...")
connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={db_host},{db_port};"
        f"DATABASE={db_name};"
        f"UID={db_user};"
        f"PWD={db_password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )

params = urllib.parse.quote_plus(connection_string)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# 4. Ingest data into the raw table
table_name = 'TBL_SC_FLEET_HIST_RAW'
print(f"Ingesting {len(df_legacy)} rows into {table_name}...")

# Use if_exists='replace' for the initial load, but remember that the agent 
# is strictly forbidden from executing any mutations itself.
try:
    df_legacy.to_sql(table_name, engine, if_exists='replace', index=False, schema='dbo')
    print("Legacy data ingestion complete!")
except Exception as e:
    print(f"Failed to ingest data: {e}")
