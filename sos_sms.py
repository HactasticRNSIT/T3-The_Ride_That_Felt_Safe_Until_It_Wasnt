"""
sos_sms.py — SafeMesh SOS SMS via Twilio
Fires a real SMS to the demo number.

Run:
  pip install twilio
  python sos_sms.py
  python sos_sms.py --repeat 2
"""

import argparse
import time
from datetime import datetime
from twilio.rest import Client

# ── Hardcoded credentials ─────────────────────────────────────────────────────

ACCOUNT_SID = "ACa51e1f3e380f151c1855e36d275bba91"
AUTH_TOKEN  = "50e73afd3f6f096dd509d935b3f6c336"
FROM_NUMBER = "+17822083730"       # your Twilio trial number
TO_NUMBER   = "+918722123585"      # recipient — verified on Twilio

MESSAGE = (
    "SafeMesh SOS — Last known location: 12.9716 N, 77.5946 E "
    "— Ride anomaly detected. Please check on the passenger. "
    "Ride ID: RIDE-20250508-BLR-4471"
)

# ── Colours ───────────────────────────────────────────────────────────────────

class C:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

# ── Sender ────────────────────────────────────────────────────────────────────

def send_sms():
    print(f"\n{C.BOLD}{C.CYAN}{'─'*55}{C.RESET}")
    print(f"  {C.BOLD}SafeMesh SOS SMS — Twilio{C.RESET}")
    print(f"{'─'*55}")
    print(f"  From    : {FROM_NUMBER}")
    print(f"  To      : {TO_NUMBER}")
    print(f"  Message : {MESSAGE}")
    print(f"  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'─'*55}")

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    msg = client.messages.create(
        body  = MESSAGE,
        from_ = FROM_NUMBER,
        to    = TO_NUMBER,
    )

    print(f"  {C.GREEN}✓  SMS sent successfully!{C.RESET}")
    print(f"     SID    : {msg.sid}")
    print(f"     Status : {msg.status}\n")
    return msg

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SafeMesh SOS SMS via Twilio")
    parser.add_argument("--repeat", type=int, default=1, help="Send N times (use 2 for demo)")
    args = parser.parse_args()

    for i in range(args.repeat):
        if args.repeat > 1:
            print(f"\n{C.BOLD}  ── Send attempt {i+1}/{args.repeat} ──{C.RESET}")
        send_sms()
        if i < args.repeat - 1:
            time.sleep(3)

if __name__ == "__main__":
    main()
