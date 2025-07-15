import os
from dotenv import load_dotenv

import gspread
from gspread import Worksheet
from google.oauth2.service_account import Credentials

load_dotenv()


def sheets_conn(which_sheet: str = None) -> Worksheet | None:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    creds = Credentials.from_service_account_file(
        "google_update/credantials.json", scopes=scopes
    )
    client = gspread.authorize(creds)

    sheet_id = (os.getenv("SHEET_ID"),)
    sheet = client.open_by_key(sheet_id).worksheet(which_sheet)

    return sheet
