from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import base64
from email.mime.text import MIMEText
from google.cloud import bigquery
from datetime import datetime, timedelta
import logging

# Налаштування логування
log_file_path = r"C:\Users\Yar14\OneDrive\Рабочий стол\script.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
logging.getLogger().addHandler(console_handler)

# Налаштування Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
credentials_path = r"C:\Users\Yar14\OneDrive\Рабочий стол\BQkey\client_secret_503070890903-58ih1bq8oljnj4tsm8tp250h7m5tmaif.apps.googleusercontent.com.json"

# Налаштування BigQuery
credentials_path_bq = r"C:/Users/Yar14/OneDrive/Рабочий стол/BQkey/yctest-447911-721cffbff5ba.json"
client = bigquery.Client.from_service_account_json(credentials_path_bq)
project_id = "yctest-447911"
dataset_id = "olefit"
table_id = "yc"

def send_email(to, subject, message_text):
    """Відправляє email."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
    logging.info(F'Message Id: {send_message["id"]}')

# Отримання дати для сортування від користувача
while True:
    try:
        date_str = input("Введіть дату у форматі YYYY-MM-DD: ")
        end_of_year = datetime.strptime(date_str, "%Y-%m-%d")
        break
    except ValueError:
        print("Невірний формат дати. Будь ласка, використовуйте формат YYYY-MM-DD.")

# Отримання email адреси  від користувача
email_to = input("Введіть email для відправлення: ")

# Отримання кількості не активних днів за які потрібно перевірити
while True:
    try:
        inactivity_period = int(input("Введіть кількість неактивних днів: "))
        if inactivity_period > 0:  # Перевірка на додатнє значення
            break
        else:
            print("Кількість днів має бути більше 0.")
    except ValueError:
        print("Невірний формат. Введіть ціле число.")

# Розрахунок дати
thirty_days_ago = end_of_year - timedelta(days=inactivity_period)

# SQL-запит (з датою останнього входу)
query = f"""
    SELECT userID, MAX(InteractionDate) as last_interaction_date, COUNT(views) as total_views
    FROM `{project_id}.{dataset_id}.{table_id}`
    GROUP BY userID
    HAVING DATE(last_interaction_date) < '{thirty_days_ago.strftime("%Y-%m-%d")}'
    ORDER BY last_interaction_date DESC
"""

try:
    # Виконання запиту
    logging.info('Виконується запит до BigQuery...')
    query_job = client.query(query)
    results = query_job.result()
    logging.info('Запит виконано успішно.')

    # Формування списку користувачів з датами останнього входу
    logging.info('Формуємо список користувачів')
    user_data = []
    for row in results:
        user_data.append(f"Користувач: {row.userID}, останній вхід: {row.last_interaction_date.strftime('%Y-%m-%d')}.")

    # Відправлення email
    if user_data:
        message = f"Користувачі, що не взаємодіяли з продуктами більше {inactivity_period} днів:\n" + "\n".join(user_data)
        send_email(email_to, "Неактивні користувачі", message)  # Використання email, введеного користувачем
        logging.info('Email зі списком надіслано успішно.')
    else:
        send_email(email_to, "Неактивні користувачі", f"Немає користувачів, що не взаємодіяли з продуктами більше {inactivity_period} днів.")
        logging.info('Немає неактивних користувачів. Email надіслано.')

except Exception as e:
    logging.error(f'Помилка: {e}')