from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import base64
import json
import mimetypes

# Phạm vi truy cập Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
FOLDER_CVS = "CVs"

def main():
    creds = None
    # Kiểm tra token xác thực
    if os.path.exists(r'src\token.json'):
        with open(r'src\token.json', 'r') as token:
            creds = json.load(token)

    # Nếu chưa có token hoặc token hết hạn, tiến hành xác thực
    if not creds or not creds.get('valid'):
        flow = InstalledAppFlow.from_client_secrets_file(r'src\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Lưu token
        with open(r'src\token.json', 'w') as token:
            token.write(creds.to_json())  # Chuyển đổi creds thành JSON

    # Kết nối tới Gmail API
    service = build('gmail', 'v1', credentials=creds)

    # Định nghĩa khoảng thời gian
    start_date = '2024/01/01'  # Ngày bắt đầu
    end_date = '2024/12/31'     # Ngày kết thúc

    # Lấy email có đính kèm CV trong khoảng thời gian
    query = f'has:attachment CV after:{start_date} before:{end_date}'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            for part in msg['payload']['parts']:
                if part['filename']:
                    print(f"Found attachment: {part['filename']}")

                    # Tải tệp đính kèm
                    attachment_id = part['body']['attachmentId']
                    attachment = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=attachment_id).execute()
                    data = attachment['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                    # Lưu tệp đính kèm
                    path = os.path.join(FOLDER_CVS, part['filename'])
                    with open(path, 'wb') as f:
                        f.write(file_data)
                    print(f"Downloaded: {path}")

if __name__ == '__main__':
    main()
