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
from config.settings import SUPABASE_TABLE
from utils.logging_config import setup_logging
from utils.error_handling import handle_errors, ErrorAction

logger = logging.getLogger(__name__)

@handle_errors(action=ErrorAction.RETURN_NONE)
def get_table_schema():
    """Get the actual column names from the Supabase table."""
    supabase = get_supabase_client()
    
    try:
        # Query just to get the column names
        response = supabase.table(SUPABASE_TABLE).select("*").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            # Get column names from the first row
            columns = list(response.data[0].keys())
            logger.debug(f"Table schema: {columns}")
            return columns
        else:
            logger.warning(f"No data in table {SUPABASE_TABLE} to determine schema")
            return []
    except Exception as e:
        logger.error(f"Error getting table schema: {e}")
        return []

@handle_errors(action=ErrorAction.RETURN_NONE)
def view_recent_measurements(days=7, limit=100):
    """
    View recent measurements from the Supabase database.
    
    Args:
        days: Number of days back to look
        limit: Maximum number of records to return
    """
    supabase = get_supabase_client()
    
    try:
        # First get the schema to find column names
        columns = get_table_schema()
        
        if not columns:
            # If we can't determine schema, try simple query with all columns
            response = supabase.table(SUPABASE_TABLE).select("*").limit(limit).execute()
            rows = response.data
            
            if not rows:
                print(f"No data found in table {SUPABASE_TABLE}")
                return []
                
            print("\n" + "="*100)
            print(f"Table columns: {list(rows[0].keys())}")
            print("-"*100)
            
            for row in rows:
                print(f"Row data: {row}")
            
            print("="*100)
            print(f"Showing {len(rows)} records")
            return rows
        
        # Try to identify time-related column for sorting
        time_col = next((col for col in columns if col.lower() in ['created_at', 'timestamp', 'time', 'date']), None)
        
        # Build query based on available columns
        query = supabase.table(SUPABASE_TABLE).select("*").limit(limit)
        
        # Add time filtering if possible
        if time_col:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            try:
                query = query.gte(time_col, start_date)
                query = query.order(time_col, desc=True)
            except:
                logger.warning(f"Could not filter by {time_col}, using basic query")
        
        # Execute the query
        response = query.execute()
        rows = response.data
        
        if not rows:
            print(f"No measurements found.")
            return []
        
        # Display the data based on actual columns
        print("\n" + "="*100)
        print(f"Available columns: {columns}")
        print("-"*100)
        
        for row in rows:
            print(f"Row data: {row}")
        
        print("="*100)
        print(f"Showing {len(rows)} records")
        return rows
        
    except Exception as e:
        print(f"Error retrieving data: {e}")
        logger.error(f"Error retrieving data: {e}", exc_info=True)
        return []

@handle_errors(action=ErrorAction.RETURN_NONE)
def backup_database_to_csv(filename=None):
    """Export the entire database to a CSV file for backup."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lcr_measurements_backup_{timestamp}.csv"
    
    supabase = get_supabase_client()
    
    try:
        # Query all data using * to get whatever columns exist
        response = supabase.table(SUPABASE_TABLE).select("*").execute()
        rows = response.data
        
        if not rows:
            print("No data to export.")
            return False
        
        # Get column names from the first row
        columns = list(rows[0].keys())
        
        # Write to CSV using actual column names
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header with actual column names
            writer.writerow(columns)
            # Write data
            for row in rows:
                writer.writerow([row.get(col, '') for col in columns])
        
        print(f"Exported {len(rows)} records to {filename}")
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