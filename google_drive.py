"""
Upload automatique des PDF vers Google Drive
Utilise un compte de service (Service Account)
"""

import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service(credentials_dict: dict):
    """Crée le service Google Drive depuis les credentials."""
    creds = service_account.Credentials.from_service_account_info(
        credentials_dict, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def upload_pdf(pdf_path: str, folder_id: str, credentials_dict: dict) -> str:
    """
    Upload un PDF vers un dossier Google Drive.
    Retourne le lien de partage du fichier.
    """
    service = get_drive_service(credentials_dict)
    filename = os.path.basename(pdf_path)

    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    media = MediaFileUpload(pdf_path, mimetype="application/pdf")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    # Rendre le fichier accessible en lecture
    service.permissions().create(
        fileId=file["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return file.get("webViewLink", "")
