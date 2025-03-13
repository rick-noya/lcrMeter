"""
Module for handling sample management operations via Supabase.
"""
import logging
from typing import List, Optional
from components.supabase_db import get_supabase_client
from config.settings import SAMPLES_TABLE  # Updated to use SAMPLES_TABLE

logger = logging.getLogger(__name__)

def get_sample_names() -> List[str]:
    """
    Get a list of unique sample names from Supabase database.
    
    Returns:
        List of unique sample names
    """
    logger.debug("Fetching sample names from Supabase")
    
    try:
        supabase = get_supabase_client()
        
        # Fetch all sample names directly from samples table
        response = supabase.table(SAMPLES_TABLE).select("sample_name").execute()
        
        # Create a set for unique sample names (removing duplicates)
        unique_samples = set()
        
        # Process results
        if response.data:
            for item in response.data:
                if item.get("sample_name") and item["sample_name"].strip():
                    unique_samples.add(item["sample_name"].strip())
        
        # Convert to sorted list
        sample_list = sorted(list(unique_samples))
        logger.debug(f"Found {len(sample_list)} unique sample names")
        return sample_list
        
    except Exception as e:
        logger.error(f"Error fetching sample names: {e}", exc_info=True)
        return []