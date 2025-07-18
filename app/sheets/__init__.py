import os
import gspread
from gspread import Worksheet
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()


async def sheets_conn(which_sheet: str = None) -> Worksheet | None:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    creds = Credentials.from_service_account_file(
        "app/sheets/credantials.json", scopes=scopes
    )
    client = gspread.authorize(creds)

    sheet_id: str = os.getenv("SHEET_ID")

    try:
        sheet: Worksheet = client.open_by_key(sheet_id).worksheet(which_sheet)
        return sheet
    except gspread.exceptions.WorksheetNotFound:
        return None
