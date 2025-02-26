import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
from config.settings import GOOGLE_SHEETS_CREDENTIALS_FILE, SPREADSHEET_ID, SHEET_RANGE

def get_sheets_service():
    logging.debug("Initializing Google Sheets service.")
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    logging.debug("Google Sheets service initialized.")
    return service

def read_sheet_values(spreadsheet_id, sheet_range):
    logging.debug("Reading sheet values from spreadsheet_id=%s, range=%s", spreadsheet_id, sheet_range)
    service = get_sheets_service()
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=sheet_range).execute()
        values = result.get('values', [])
        logging.debug("Fetched %d rows from the sheet.", len(values))
        return values
    except Exception as e:
        logging.error("Error reading sheet values: %s", e)
        raise

def append_rows_to_sheet(spreadsheet_id, sheet_range, rows):
    logging.debug("Appending %d rows to spreadsheet_id=%s, range=%s", len(rows), spreadsheet_id, sheet_range)
    service = get_sheets_service()
    body = {'values': rows}
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption='USER_ENTERED',
            body=body).execute()
        logging.debug("Rows appended successfully.")
    except Exception as e:
        logging.error("Error appending rows to sheet: %s", e)
        raise

def get_sample_names():
    logging.debug("Fetching sample names from the sheet.")
    values = read_sheet_values(SPREADSHEET_ID, SHEET_RANGE)
    sample_names = set()
    for row in values[1:]:  # Skip the header row
        if len(row) > 1:
            sample_names.add(row[1])
    sample_names_list = list(sample_names)
    logging.debug("Found sample names: %s", sample_names_list)
    return sample_names_list

async def upload_data(main_window):
    if not main_window.lcr_data:
        main_window.append_log("No data to upload.")
        return
    header = ["Timestamp", "Sample Name", "Test Type", "Value 1", "Value 2"]
    try:
        logging.debug("Reading existing sheet values before upload.")
        existing_values = read_sheet_values(SPREADSHEET_ID, SHEET_RANGE)
    except Exception as e:
        main_window.append_log(f"Error reading sheet: {e}")
        return
    sheet_is_empty = (len(existing_values) == 0)
    if sheet_is_empty:
        rows = [header] + main_window.lcr_data
    else:
        rows = main_window.lcr_data
    try:
        logging.debug("Uploading data to Google Sheets.")
        append_rows_to_sheet(SPREADSHEET_ID, SHEET_RANGE, rows)
        main_window.append_log("Data successfully appended to Google Sheets.")
        logging.debug("Data upload successful.")
    except Exception as e:
        main_window.append_log(f"Error appending data: {e}")
        logging.error("Error appending data to sheet: %s", e)