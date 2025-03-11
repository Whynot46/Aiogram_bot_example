import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
from bot.config import Config
import pandas as pd
from bot.database.db import update_all_user_status
import httplib2


# Аутентификация через Service Account
creds_service = ServiceAccountCredentials.from_json_keyfile_name(Config.GOOGLE_CREDENTIALS_PATH, scopes=Config.GOOGLE_SCOPES).authorize(httplib2.Http())

# Создание сервисов для работы с Google Drive и Google Sheets
drive_service = build('drive', 'v3', http=creds_service)
sheets_service = build('sheets', 'v4', http=creds_service)


# Загрузка файла на Google Drive
async def upload_file(file_path : str, folder_id : str =Config.GOOGLE_MEDIA_FOLDER_ID):
    try:
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id] if folder_id else []
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        file_id = file.get('id')
        file_url = f"https://drive.google.com/file/d/{file_id}/view"

        return file_url
    except Exception as error:
        print(f"Ошибка при загрузке файла: {error}")


# Удаление локального файла
async def delete_local_file(file_path):
    try:
        os.remove(file_path)
    except Exception as error:
        print(f"Ошибка при удалении локального файла {file_path}: {error}")


# Добавление строки в Google Sheet
async def upload_report(report_data):
    try:
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

    except Exception as error:
        print(f"Ошибка при добавлении данных в Google Таблицу: {error}")


# Обновления списка пользователей из справочника в Google Sheets
async def update_users():
    try:
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

    except Exception as error:
        print(f"Ошибка при чтении Google Таблицы: {error}")
