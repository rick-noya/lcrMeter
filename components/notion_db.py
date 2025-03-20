import logging
from typing import Dict, Any, Optional
from notion_client import Client

from config.settings import NOTION_SECRET, NOTION_DATABASE_ID
from utils.error_handling import handle_errors, ErrorAction

logger = logging.getLogger(__name__)

# Global notion client
_notion_client = None

def get_notion_client() -> Client:
    """Initialize and return the Notion client."""
    global _notion_client
    if _notion_client is None:
        logger.debug("Initializing Notion client")
        _notion_client = Client(auth=NOTION_SECRET)
        logger.debug("Notion client initialized successfully")
    return _notion_client

@handle_errors(action=ErrorAction.RERAISE)
def find_page_by_sample_name(sample_name: str) -> Optional[str]:
    """
    Find a page in the Notion database by sample name.
    Returns the page ID if found, None otherwise.
    Uses the property "Sorbent Sample Name" for queries.
    """
    notion = get_notion_client()
    
    # Query for pages with matching sample name
    query = {
        "filter": {
            "property": "Sorbent Sample Name",
            "title": {
                "equals": sample_name
            }
        }
    }
    
    response = notion.databases.query(database_id=NOTION_DATABASE_ID, **query)
    
    if response["results"]:
        # Return the first matching page ID
        return response["results"][0]["id"]
    
    return None

@handle_errors(action=ErrorAction.RERAISE)
def update_or_create_page(sample_name: str, resistance_value: float) -> str:
    """
    Update or create a page in the Notion database with the given sample name and resistance value.
    Uses the properties "Sorbent Sample Name" for the sample identifier and "Resistance" for the measurement.
    Returns the page ID.
    """
    notion = get_notion_client()
    
    # First, check if the page already exists
    page_id = find_page_by_sample_name(sample_name)
    
    if page_id:
        # Update existing page
        logger.debug(f"Updating existing Notion page for sample '{sample_name}'")
        notion.pages.update(
            page_id=page_id, 
            properties={
                "Resistance": {
                    "number": float(resistance_value)
                }
            }
        )
        return page_id
    else:
        # Create new page
        logger.debug(f"Creating new Notion page for sample '{sample_name}'")
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Sorbent Sample Name": {
                    "title": [
                        {
                            "text": {
                                "content": sample_name
                            }
                        }
                    ]
                },
                "Resistance": {
                    "number": float(resistance_value)
                }
            }
        )
        return response["id"]

@handle_errors(action=ErrorAction.RERAISE)
async def upload_measurement_to_notion(main_window, sample_name: str, resistance_value: float):
    """
    Upload a measurement to Notion.
    Runs the API call in a separate thread to avoid blocking the UI.
    """
    from utils.error_handling import to_thread_with_error_handling
    
    try:
        logger.debug(f"Uploading measurement for '{sample_name}' to Notion")
        
        # Run the Notion API call in a thread to avoid blocking
        page_id = await to_thread_with_error_handling(
            update_or_create_page,
            sample_name,
            resistance_value,
            error_message="Failed to upload to Notion",
            ui_logger=main_window.append_log
        )
        
        if page_id:
            main_window.append_log(f"Data successfully saved to Notion for sample '{sample_name}'")
            logger.debug(f"Notion update successful, page ID: {page_id}")
        else:
            main_window.append_log("Failed to save data to Notion")
            logger.error("Notion update returned no page ID")
    
    except Exception as e:
        main_window.append_log(f"Error saving data to Notion: {e}")
        logger.error(f"Error uploading data to Notion: {e}")