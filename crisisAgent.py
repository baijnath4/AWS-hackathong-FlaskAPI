from dotenv import load_dotenv
import os
import pandas as pd
import smtplib
from email.message import EmailMessage
from typing import List

# Load environment variables from .env
load_dotenv()

def filter_by_date(target_date: str) -> List[dict]:
    file_path = "resource_allocation_mock.csv"

    try:
        # Validate the date format
        pd.to_datetime(target_date, format='%d-%m-%Y')

        # Load data
        df = pd.read_csv(file_path)

        if 'Date' not in df.columns:
            raise KeyError("The 'Date' column is missing.")

        df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.strftime("%d-%m-%Y")
        filtered_df = df[df['Date'] == target_date]

        if filtered_df.empty:
            raise ValueError(f"No records found for date: {target_date}")

        return filtered_df.to_dict(orient="records")

    except Exception as e:
        print(f"Error: {e}")
        return []

# target_date= "04-06-2025"
# aa = filter_by_date(target_date)
# print(aa)

def send_email(subject: str, recipient: str, body: str) -> str:
    try:
        sender = os.getenv("email_sender")
        password = os.getenv("email_password")
        smtp_server = os.getenv("smtp_server", "smtp.gmail.com")
        smtp_port = int(os.getenv("smtp_port", 587))

        if not sender or not password:
            raise EnvironmentError("Missing email credentials in environment variables.")

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        return "Email sent successfully!"

    except Exception as e:
        print(f"Email Error: {e}")
        return "Failed to send email."


# records = filter_by_date("04-06-2025")
# if records:
#     status = send_email(
#         subject="Filtered Resource Data",
#         recipient="baijkuma@in.ibm.com",
#         body=str(records)
#     )
#     print(status)
# else:
#     print("No data found for the given date.")
