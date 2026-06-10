"""
Send Bali welcome emails to 9 travelers.
Dry run by default. Pass --send to actually send.

Usage:
  python send_welcome.py          # dry run
  python send_welcome.py --send   # send for real
"""

import os
import sys
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SENDER_NAME = "Monet Planter"
SENDER_EMAIL = os.getenv("CONTACT_GMAIL_USER", "contact@escapefromrealitytravelers.com")
APP_PASSWORD = os.getenv("CONTACT_GMAIL_APP_PASSWORD")
SUBJECT = "Your Bali Trip App is Ready 🌴"

TRAVELERS = [
    ("Pamela",   "Washington",  "pamscott.w@gmail.com"),
    ("Cindy",    "Notti",       "cnotti@hotmail.com"),
    ("Veronica", "Barnes",      "veronica.barnes25@gmail.com"),
    ("Francine", "Applewhite",  "f_applewhite@yahoo.com"),
    ("Lorine",   "Hall",        "hallaktrans2@gmail.com"),
    ("Lourdes",  "Bernal",      "lbernal0101@gmail.com"),
    ("Tiana",    "Towns",       "tianamtowns@gmail.com"),
    ("Cynthia",  "Franklin",    "cfrankamis@gmail.com"),
    ("Judy",     "Jackson",     "jackson.jj0507@gmail.com"),
]


def build_body(first_name: str, email: str) -> str:
    return f"""Good afternoon {first_name},

The countdown is on and I want to make sure you have everything you need before you go.

Your private travel portal for the Bali Retirement Trip (June 23 to July 3, 2026) is live and ready for you.

Sign in here: https://bali.escapefromrealitytravel.com

Your login details:
  Email: {email}
  Temporary password: Bali2026!

Once you are signed in please take a moment to update your password using the link in the top right corner of the app.

Inside you will find everything you need for the trip including your group chat, full itinerary, hotel and transfer details, and a direct line to me for anything that comes up while you are traveling.

In the meantime if you have any questions at all please do not hesitate to reach out.

We are almost there ladies. Get ready for the trip of a lifetime!


Kind regards,

Monet Planter
Lead Operations and Strategy Director | Owner
(ACC) Accredited Cruise Counselor | (CTA) Certified Travel Associate
Escape From Reality Travel LLC
803-814-5792
www.escapefromrealitytravel.com
"""


def dry_run():
    print("=" * 60)
    print("DRY RUN — no emails will be sent")
    print("=" * 60)
    print(f"From:    {SENDER_NAME} <{SENDER_EMAIL}>")
    print(f"Subject: {SUBJECT}")
    print()
    for i, (first, last, email) in enumerate(TRAVELERS, 1):
        print(f"  {i}. {first} {last} <{email}>")
    print()
    print("--- Preview (first traveler) ---")
    print(build_body(TRAVELERS[0][0], TRAVELERS[0][2]))
    print("=" * 60)
    print(f"Total: {len(TRAVELERS)} emails ready to send.")
    print("Run with --send to deliver.")


def send_all():
    if not APP_PASSWORD:
        print("ERROR: CONTACT_GMAIL_APP_PASSWORD is not set.")
        sys.exit(1)

    print(f"Connecting to Gmail SMTP as {SENDER_EMAIL}...")
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        print("Authenticated.\n")
    except Exception as e:
        print(f"SMTP login failed: {e}")
        sys.exit(1)

    ok, failed = 0, []
    for first, last, email in TRAVELERS:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = SUBJECT
        msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg["To"] = email
        msg.attach(MIMEText(build_body(first, email), "plain"))
        try:
            server.sendmail(SENDER_EMAIL, email, msg.as_string())
            print(f"  ✓ {first} {last} <{email}>")
            ok += 1
            time.sleep(1)  # avoid rate limiting
        except Exception as e:
            print(f"  ✗ {first} {last} <{email}> — {e}")
            failed.append(email)

    server.quit()
    print(f"\nDone: {ok} sent, {len(failed)} failed.")
    if failed:
        print("Failed:", ", ".join(failed))


if __name__ == "__main__":
    if "--send" in sys.argv:
        send_all()
    else:
        dry_run()
