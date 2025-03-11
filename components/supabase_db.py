import logging
import os
from datetime import datetime
from typing import List, Any
from supabase import create_client, Client
import atexit

from config.settings import (
    SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE,
    DB_ENABLE
)
from utils.error_handling import handle_errors, ErrorAction

logger = logging.getLogger(__name__)

# Global supabase client
_supabase_client = None

def cleanup_resources():
    """Clean up global resources like database connections."""
    global _supabase_client
    if _supabase_client is not None:
        logger.debug("Closing Supabase client connection")
        _supabase_client = None

# Register cleanup function to run at application exit
atexit.register(cleanup_resources)

@handle_errors(action=ErrorAction.RERAISE)
def get_supabase_client() -> Client:
    """
    Get or initialize the Supabase client.
    
    Returns:
        Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        logger.debug("Initializing Supabase client")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.debug("Supabase client initialized successfully")
    
    return _supabase_client

@handle_errors(action=ErrorAction.RERAISE)
def verify_table_exists() -> bool:
    """
    Verify that the measurements table exists in Supabase.
    Uses a simple query that doesn't assume specific column structure.
    
    Returns:
        True if verification was successful
    """
    try:
        supabase = get_supabase_client()
        # Just query using * to avoid specifying column names
        response = supabase.table(SUPABASE_TABLE).select("*").limit(1).execute()
        logger.debug("Supabase table verification successful")
        
        # Log table structure if we got data
        if response.data and len(response.data) > 0:
            columns = list(response.data[0].keys())
            logger.info(f"Supabase table columns: {columns}")
        
        return True
    except Exception as e:
        logger.error(f"Supabase table verification failed: {e}")
        error_msg = str(e)
        if "does not exist" in error_msg:
            logger.error(f"Table '{SUPABASE_TABLE}' does not exist in Supabase")
        raise

@handle_errors(action=ErrorAction.RERAISE)
def append_rows_to_database(rows):
    """
    Append measurement rows to the Supabase database.
    
    Args:
        rows: List of measurement data rows in the format:
            [timestamp, sample_name, test_type, value1, value2, tester_name]
    """
    logger.debug(f"Appending {len(rows)} rows to Supabase database")
    supabase = get_supabase_client()
    data_to_insert = []
    
    # First query database to get actual column names
    try:
        response = supabase.table(SUPABASE_TABLE).select("*").limit(1).execute()
        if response.data and len(response.data) > 0:
            columns = list(response.data[0].keys())
            logger.debug(f"Detected database columns: {columns}")
        else:
            # Default to known column names from error message
            columns = ["id", "created_at", "sample_name", "test_type", "impedance", "resistance", "tester"]
            logger.debug(f"Using default column mapping: {columns}")
    except Exception as e:
        logger.warning(f"Could not fetch column names: {e}")
        # Default to known column names from error message
        columns = ["id", "created_at", "sample_name", "test_type", "impedance", "resistance", "tester"]
        logger.debug(f"Using default column mapping: {columns}")
    
    for row in rows:
        measurement = {}
        
        # Always safe fields
        measurement["created_at"] = row[0] if isinstance(row[0], str) else row[0].isoformat()
        measurement["sample_name"] = row[1]
        
        if "test_type" in columns:
            measurement["test_type"] = row[2]
        
        # Map inductance to impedance column
        if "impedance" in columns:
            measurement["impedance"] = row[3]  # This is the L value
        
        # Map resistance to resistance column
        if "resistance" in columns:
            measurement["resistance"] = row[4]  # This is the R value
        
        # Tester name
        if len(row) > 5 and "tester" in columns:
            measurement["tester"] = row[5]
        
        data_to_insert.append(measurement)
    
    # Insert the data
    try:
        response = supabase.table(SUPABASE_TABLE).insert(data_to_insert).execute()
        logger.debug("Rows appended to Supabase database successfully")
    except Exception as e:
        logger.warning(f"Database insertion failed: {e}")
        
        # Try a minimal insert with just the essential fields
        try:
            minimal_data = []
            for row in rows:
                data = {
                    "sample_name": row[1],
                }
                
                # Only add fields that we know exist
                if "impedance" in columns:
                    data["impedance"] = row[3]
                    
                if "resistance" in columns:
                    data["resistance"] = row[4]
                
                minimal_data.append(data)
            
            response = supabase.table(SUPABASE_TABLE).insert(minimal_data).execute()
            logger.debug("Minimal rows appended to Supabase database")
        except Exception as e2:
            logger.error(f"Final fallback insertion failed: {e2}")
            raise e  # Re-raise the original error

@handle_errors(action=ErrorAction.RERAISE)
async def upload_data(main_window):
    """
    Upload measurement data from main_window to the Supabase database.
    
    Args:
        main_window: The main application window containing lcr_data.
    """
    if not DB_ENABLE:
        main_window.append_log("Database storage is disabled in settings")
        return
        
    if not main_window.lcr_data:
        main_window.append_log("No data to upload to database")
        return
    
    try:
        logger.debug("Uploading data to Supabase database")
        append_rows_to_database(main_window.lcr_data)
        main_window.append_log("Data successfully saved to Supabase database")
        logger.debug("Data upload to Supabase database successful")
    except Exception as e:
        main_window.append_log(f"Error saving data to Supabase database: {e}")
        logger.error(f"Error uploading data to Supabase database: {e}")