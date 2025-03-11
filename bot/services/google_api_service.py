import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
from bot.config import Config
import pandas as pd
from bot.db import update_all_user_status
import httplib2
from bot.logger import logger, error_handler


try:
    # Аутентификация через Service Account
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(Config.GOOGLE_CREDENTIALS_PATH, scopes=Config.GOOGLE_SCOPES).authorize(httplib2.Http())

    # Создание сервисов для работы с Google Drive и Google Sheets
    drive_service = build('drive', 'v3', http=creds_service)
    sheets_service = build('sheets', 'v4', http=creds_service)
except Exception as error:
    logger.error(f"Аутентификация Service Account: {error}", exc_info=True)


# Загрузка файла на Google Drive
@error_handler
async def upload_file(file_path : str, folder_id : str =Config.GOOGLE_MEDIA_FOLDER_ID):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id] if folder_id else []
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    file_id = file.get('id')
    file_url = f"https://drive.google.com/file/d/{file_id}/view"

    return file_url


# Удаление локального файла
@error_handler
async def delete_local_file(file_path):
    os.remove(file_path)


# Добавление строки в Google Sheet
@error_handler
async def upload_report(report_data):
    sheet_name = report_data.get("stage", "")
    range_name = f"{sheet_name}!A:Z"

    body = {
        'values': [list(report_data.values())]
    }

    sheets_service.spreadsheets().values().append(
        spreadsheetId=Config.GOOGLE_REPORTS_FILE_ID,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()


# Обновления списка пользователей из справочника в Google Sheets
@error_handler
async def update_users():
    sheet_name = "СОТРУДНИКИ"
    range_name = f"{sheet_name}!A:Z"
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=Config.GOOGLE_DIRECTORY_ID,
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    if not values:
        return
    
    df_employees = pd.DataFrame(values[1:], columns=values[0])
    employees_data = df_employees.to_dict(orient="records")
    
    await update_all_user_status(employees_data)
