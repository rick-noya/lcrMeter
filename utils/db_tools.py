"""
Utility functions for Supabase database management
"""
import sys
import os
import logging
from datetime import datetime, timedelta
import csv
from typing import List, Dict

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.supabase_db import get_supabase_client
from config.settings import SAMPLES_TABLE, MEASUREMENTS_TABLE
from utils.logging_config import setup_logging
from utils.error_handling import handle_errors, ErrorAction

logger = logging.getLogger(__name__)

@handle_errors(action=ErrorAction.RETURN_NONE)
def get_table_schema(table_name=MEASUREMENTS_TABLE):
    """Get the actual column names from the specified Supabase table."""
    supabase = get_supabase_client()
    
    try:
        # Query just to get the column names
        response = supabase.table(table_name).select("*").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            # Get column names from the first row
            columns = list(response.data[0].keys())
            logger.debug(f"Table schema for {table_name}: {columns}")
            return columns
        else:
            logger.warning(f"No data in table {table_name} to determine schema")
            return []
    except Exception as e:
        logger.error(f"Error getting table schema for {table_name}: {e}")
        return []

@handle_errors(action=ErrorAction.RETURN_NONE)
def view_recent_measurements(days=None, limit=1000):
    """
    View measurements from the Supabase database with normalized schema.
    
    Args:
        days: Number of days back to look (None for all data)
        limit: Maximum number of records to return
    """
    supabase = get_supabase_client()
    
    try:
        # Build the measurements query
        measurements_query = (supabase.table(MEASUREMENTS_TABLE)
            .select("id,created_at,sample_id,test_type,impedance,resistance,tester,gui_version")
            .order("created_at", desc=True)
            .limit(limit))
            
        # Only apply date filter if days is specified
        if days is not None:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            measurements_query = measurements_query.gte("created_at", start_date)
        
        # Execute the query
        measurements_resp = measurements_query.execute()
        measurements = measurements_resp.data
        
        if not measurements:
            logger.info("No measurements found.")
            return []
        
        # Get all sample_ids from the returned measurements
        sample_ids = [m["sample_id"] for m in measurements]
        
        # Fetch all relevant samples in one query
        samples_resp = (supabase.table(SAMPLES_TABLE)
            .select("id,sample_name")
            .in_("id", sample_ids)
            .execute())
        
        samples = samples_resp.data
        
        # Create a map of sample_id to sample_name
        sample_map = {sample["id"]: sample["sample_name"] for sample in samples}
        
        # Join the data manually in Python
        joined_data = []
        for measurement in measurements:
            sample_id = measurement["sample_id"]
            sample_name = sample_map.get(sample_id, "Unknown Sample")
            
            joined_data.append({
                "id": measurement["id"],
                "created_at": measurement["created_at"],
                "sample_name": sample_name,
                "test_type": measurement["test_type"],
                "impedance": measurement["impedance"],
                "resistance": measurement["resistance"],
                "tester": measurement["tester"],
                "gui_version": measurement.get("gui_version", "")
            })
        
        # Display the data
        print("\n" + "="*100)
        if joined_data:
            print(f"Available columns: {list(joined_data[0].keys())}")
        print("-"*100)
        
        for row in joined_data:
            print(f"Row data: {row}")
        
        print("="*100)
        print(f"Showing {len(joined_data)} records")
        return joined_data
        
    except Exception as e:
        print(f"Error retrieving data: {e}")
        logger.error(f"Error retrieving data: {e}", exc_info=True)
        return []

@handle_errors(action=ErrorAction.RETURN_NONE)
def backup_database_to_csv(filename=None):
    """Export the measurements data with joined sample names to a CSV file for backup."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lcr_measurements_backup_{timestamp}.csv"
    
    # Use our modified function to get the joined data
    joined_data = view_recent_measurements(days=36500, limit=100000)  # Very large values to get all data
    
    if not joined_data:
        print("No data to export.")
        return False
    
    try:
        # Get column names from the first row
        columns = list(joined_data[0].keys())
        
        # Write to CSV using actual column names
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header with actual column names
            writer.writerow(columns)
            # Write data
            for row in joined_data:
                writer.writerow([row.get(col, '') for col in columns])
        
        print(f"Exported {len(joined_data)} records to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return False

if __name__ == "__main__":
    setup_logging()
    
    # Command line argument parsing
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "view":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            view_recent_measurements(days)
        elif command == "backup":
            filename = sys.argv[2] if len(sys.argv) > 2 else None
            backup_database_to_csv(filename)
        else:
            print("Unknown command. Available commands: view, backup")
            print("Examples:")
            print("  python db_tools.py view 30    # View last 30 days of data")
            print("  python db_tools.py backup     # Backup to auto-named file")
            print("  python db_tools.py backup file.csv  # Backup to specific file")
    else:
        # Default action: show recent measurements
        view_recent_measurements()