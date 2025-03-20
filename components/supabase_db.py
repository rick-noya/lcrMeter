import logging
import os
from datetime import datetime
from typing import List, Any
from supabase import create_client, Client
import atexit

from config.settings import (
    SUPABASE_URL, SUPABASE_KEY, SAMPLES_TABLE, MEASUREMENTS_TABLE,
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
    
    if (_supabase_client is None):
        logger.debug("Initializing Supabase client")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.debug("Supabase client initialized successfully")
    
    return _supabase_client

@handle_errors(action=ErrorAction.RERAISE)
def verify_table_exists() -> bool:
    """
    Verify that the necessary tables exist in Supabase.
    
    Returns:
        True if verification was successful
    """
    try:
        supabase = get_supabase_client()
        # Verify the measurements table (samples should exist too)
        response = supabase.table(MEASUREMENTS_TABLE).select("*").limit(1).execute()
        logger.debug("Supabase measurements table verification successful")
        
        # Log table structure if we got data
        if response.data and len(response.data) > 0:
            columns = list(response.data[0].keys())
            logger.info(f"Measurements table columns: {columns}")
        
        return True
    except Exception as e:
        logger.error(f"Supabase table verification failed: {e}")
        error_msg = str(e)
        if "does not exist" in error_msg:
            logger.error(f"Table '{MEASUREMENTS_TABLE}' does not exist in Supabase")
        raise

@handle_errors(action=ErrorAction.RERAISE)
def append_rows_to_database(rows: List[List[Any]]):
    """
    For each measurement record, find (or insert) the sample and then insert the measurement.
    Each row is in the format:
        [timestamp, sample_name, test_type, inductance, resistance, tester_name, gui_version]
    """
    logger.debug(f"Appending {len(rows)} measurement rows to Supabase database")
    supabase = get_supabase_client()
    measurements_to_insert = []
    
    for row in rows:
        # Extract fields from the row
        # Assumes: row[0]=timestamp, row[1]=sample_name, row[2]=test_type,
        # row[3]=inductance, row[4]=resistance, row[5]=tester_name, row[6]=gui_version
        timestamp = row[0] if isinstance(row[0], str) else row[0].isoformat()
        sample_name = row[1].strip() if row[1] else ""
        test_type = row[2]
        inductance = row[3]  # Changed from impedance
        resistance = row[4]
        tester = row[5] if len(row) >= 6 else ""
        gui_version = row[6] if len(row) >= 7 else ""
        
        # Look up the sample in the SAMPLES_TABLE
        sample_resp = supabase.table(SAMPLES_TABLE).select("id").eq("sample_name", sample_name).execute()
        if sample_resp.data and len(sample_resp.data) > 0:
            sample_id = sample_resp.data[0]["id"]
        else:
            # Insert the sample if not present
            insert_sample = supabase.table(SAMPLES_TABLE).insert({"sample_name": sample_name}).execute()
            if insert_sample.data and len(insert_sample.data) > 0:
                sample_id = insert_sample.data[0]["id"]
            else:
                logger.error(f"Failed to insert sample '{sample_name}'. Skipping measurement.")
                continue  # Skip adding this measurement record
        
        measurement = {
            "created_at": timestamp,
            "sample_id": sample_id,
            "test_type": test_type,
            "inductance": inductance,  # Changed from impedance
            "resistance": resistance,
            "tester": tester,
            "gui_version": gui_version
        }
        measurements_to_insert.append(measurement)
    
    if measurements_to_insert:
        try:
            response = supabase.table(MEASUREMENTS_TABLE).insert(measurements_to_insert).execute()
            logger.debug("Measurements inserted successfully into Supabase")
        except Exception as e:
            logger.error(f"Failed inserting measurements: {e}")
            raise
    else:
        logger.debug("No new measurement records to insert.")

@handle_errors(action=ErrorAction.RERAISE)
async def upload_data(main_window):
    """
    Upload measurement data from main_window to Supabase and Notion.
    """
    if not DB_ENABLE:
        main_window.append_log("Database storage is disabled in settings")
        return

    if not main_window.lcr_data:
        main_window.append_log("No data to upload to database")
        return

    # Check if LCR meter is still connected
    if hasattr(main_window, 'lcr_meter') and not main_window.lcr_meter.instrument:
        # LCR meter reference exists but connection is closed
        reply = QMessageBox.question(
            main_window,
            "Device Connection Warning",
            "The LCR meter appears to be disconnected. This may indicate a measurement error.\n\n"
            "Do you want to save this data anyway?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            main_window.append_log("Data upload canceled due to device connection issue.")
            return
            
        main_window.append_log("Proceeding with data upload despite device connection warning.")

    try:
        # Upload to Supabase
        logger.debug("Uploading measurement data to Supabase database")
        append_rows_to_database(main_window.lcr_data)
        main_window.append_log("Data successfully saved to Supabase database")
        logger.debug("Data upload to Supabase successful")
        
        # Now upload to Notion (only if enabled)
        from components.notion_db import upload_measurement_to_notion
        from config.settings import NOTION_ENABLE
        
        if NOTION_ENABLE:
            for row in main_window.lcr_data:
                sample_name = row[1]  # Sample name
                resistance_str = row[4]  # Resistance value as string
                
                # Convert resistance string to float
                try:
                    resistance_value = float(resistance_str)
                except (ValueError, AttributeError):
                    logger.error(f"Could not parse resistance value: {resistance_str}")
                    resistance_value = 0.0
                    
                await upload_measurement_to_notion(main_window, sample_name, resistance_value)
        
    except Exception as e:
        main_window.append_log(f"Error saving data: {e}")
        logger.error(f"Error uploading data: {e}")

@handle_errors(action=ErrorAction.RERAISE)
def create_normalized_schema():
    """
    Create the normalized database schema if it doesn't exist.
    This includes samples and measurements tables.
    """
    logger.debug("Attempting to create or verify normalized database schema")
    supabase = get_supabase_client()
    
    try:
        # Using SQL through Supabase's RPC to create the schema
        
        # 1. Create the immutable date truncation function
        create_func_query = """
        CREATE OR REPLACE FUNCTION immutable_date_trunc_minutes(ts TIMESTAMPTZ)
        RETURNS TIMESTAMPTZ
        IMMUTABLE STRICT LANGUAGE SQL AS $$
            SELECT date_trunc('minute', ts);
        $$;
        """
        
        # 2. Create samples table
        create_samples_query = f"""
        CREATE TABLE IF NOT EXISTS {SAMPLES_TABLE} (
            id SERIAL PRIMARY KEY,
            sample_name TEXT NOT NULL UNIQUE
        )
        """
        
        # 3. Create measurements table
        create_measurements_query = f"""
        CREATE TABLE IF NOT EXISTS {MEASUREMENTS_TABLE} (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            sample_id INTEGER NOT NULL REFERENCES {SAMPLES_TABLE}(id) ON DELETE CASCADE,
            test_type TEXT NOT NULL,
            inductance TEXT NOT NULL,  
            resistance TEXT NOT NULL,
            tester TEXT NOT NULL,
            gui_version TEXT,
            normalized_timestamp TIMESTAMPTZ GENERATED ALWAYS AS (immutable_date_trunc_minutes(created_at)) STORED,
            CONSTRAINT unique_measurement UNIQUE (sample_id, test_type, normalized_timestamp)
        )
        """
        
        # 4. Create indexes
        create_indexes_query = f"""
        CREATE INDEX IF NOT EXISTS idx_measurements_sample_id ON {MEASUREMENTS_TABLE} (sample_id);
        CREATE INDEX IF NOT EXISTS idx_measurements_created_at ON {MEASUREMENTS_TABLE} (created_at)
        """
        
        # Execute the queries
        logger.debug("Creating immutable date truncation function")
        supabase.rpc('run_query', {"query": create_func_query}).execute()
        
        logger.debug(f"Creating samples table: {SAMPLES_TABLE}")
        supabase.rpc('run_query', {"query": create_samples_query}).execute()
        
        logger.debug(f"Creating measurements table: {MEASUREMENTS_TABLE}")
        supabase.rpc('run_query', {"query": create_measurements_query}).execute()
        
        logger.debug("Creating indexes")
        supabase.rpc('run_query', {"query": create_indexes_query}).execute()
        
        logger.info("Normalized schema created or verified successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating normalized schema: {e}")
        raise