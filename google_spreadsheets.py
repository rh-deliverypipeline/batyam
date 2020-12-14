import json
import os
import tempfile
from datetime import datetime

import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
from jinja2 import FileSystemLoader, Environment


def generate_and_load_credentials():
    """Generates a json credentials file for Google API using .env and a jinja2 template files."""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('.json.j2')
    output = template.render(
        private_key_id=os.getenv('GOOGLE_PRIVATE_KEY_ID'),
        private_key=os.getenv('GOOGLE_PRIVATE_KEY')
    )
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as temp_dir:
        json_file_dir = os.path.join(temp_dir, 'google_creds.json')
        with open(json_file_dir, 'w') as jsonfile:
            json.dump(json.loads(output), jsonfile, separators=(',', ':'))
        return service_account.Credentials.from_service_account_file(json_file_dir)


credentials = generate_and_load_credentials()
scopes = credentials.with_scopes(
    [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
)


def create_spreadsheet(title, data):
    """creates a spreadsheet instance, populate it with the df values and returns it."""
    sheets_service = build("sheets", "v4", credentials=credentials)
    sheets = sheets_service.spreadsheets()
    body_content = {"properties": {"title": f"{title} - {datetime.now().date().strftime('%d/%m/%y')}"},
                    "sheets": list(map(lambda d: {"properties": {"title": d.get("title")}}, data))}
    res = sheets.create(body=body_content).execute()
    spreadsheet_id = res.get("spreadsheetId")

    def df_to_sheet(df_cc):
        """convert the DF into a matrix of the columns and values."""
        df_columns = [np.array(df_cc.columns)]
        df_values = df_cc.values.tolist()
        return np.concatenate((df_columns, df_values)).tolist()

    update_body = {
        "valueInputOption": "RAW",
        "data": list(map(lambda d: {"range": d.get("title"), "values": df_to_sheet(d.get("df"))}, data))
    }
    sheets.values().batchUpdate(spreadsheetId=spreadsheet_id, body=update_body).execute()
    return res


def post_spreadsheet(spreadsheet_id, options, notify=False):
    """Post the spreadsheet to Google drive, configure access permissions and returns the instance."""
    drive_service = build("drive", "v3", credentials=credentials)

    return (
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=options,
            sendNotificationEmail=notify,
        ).execute()
    )


def create_and_share_spreadsheet(title, df):
    """Creates a Google spreadsheet instance with DF information, set access permissions and returns it's URL."""
    data = [
        {
            "title": datetime.now().date().strftime('%d/%m/%y'),
            "df": df
        }
    ]
    permissions = {"config": {"role": "reader", "type": "domain", "domain": "redhat.com"}, "notify": False}
    sheet = create_spreadsheet(title, data)
    post_spreadsheet(sheet.get("spreadsheetId"), permissions.get("config"), permissions.get("notify"))

    return sheet.get("spreadsheetUrl").rsplit('/', 1)[0]
