"""
sos_call.py — SafeMesh SOS Voice Call via Twilio
Makes an automated call with a TwiML voice message.

Run:
  pip install twilio
  python sos_call.py
  python sos_call.py --repeat 2
"""

import argparse
import time
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# ── Hardcoded credentials ─────────────────────────────────────────────────────

ACCOUNT_SID = "ACa51e1f3e380f151c1855e36d275bba91"
AUTH_TOKEN  = "d06428ad27452c2fa9840709edb8a479"
FROM_NUMBER = "+17822083730"       # your Twilio trial number
TO_NUMBER   = "+918722123585"      # recipient — verified on Twilio

# ── TwiML voice message ───────────────────────────────────────────────────────

def build_twiml():
    response = VoiceResponse()
    response.pause(length=1)
    response.say(
        "SafeMesh emergency alert. "
        "Your contact may need assistance. "
        "Last known location has been sent to your phone. "
        "The coordinates are 12 point 97 degrees North, 77 point 59 degrees East, Bangalore. "
        "Please check on your contact immediately or call local emergency services. "
        "This is an automated message from SafeMesh ride safety. "
        "Stay safe.",
        voice="alice",
        language="en-IN",
    )
    response.pause(length=1)
    return str(response)

# ── Colours ───────────────────────────────────────────────────────────────────

class C:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

# ── Caller ────────────────────────────────────────────────────────────────────

def make_call():
    twiml = build_twiml()

    print(f"\n{C.BOLD}{C.CYAN}{'─'*55}{C.RESET}")
    print(f"  {C.BOLD}SafeMesh SOS Voice Call — Twilio{C.RESET}")
    print(f"{'─'*55}")
    print(f"  From    : {FROM_NUMBER}")
    print(f"  To      : {TO_NUMBER}")
    print(f"  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n  Voice script:")
    print(f"  \"SafeMesh emergency alert. Your contact may need assistance.\"")
    print(f"{'─'*55}")

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    call = client.calls.create(
        twiml = twiml,
        from_ = FROM_NUMBER,
        to    = TO_NUMBER,
    )

    print(f"  {C.GREEN}✓  Call dispatched successfully!{C.RESET}")
    print(f"     Call SID : {call.sid}")
    print(f"     Status   : {call.status}\n")
    return call

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SafeMesh SOS Call via Twilio Voice")
    parser.add_argument("--repeat", type=int, default=1, help="Place N calls (use 2 for demo)")
    args = parser.parse_args()

    for i in range(args.repeat):
        if args.repeat > 1:
            print(f"\n{C.BOLD}  ── Call attempt {i+1}/{args.repeat} ──{C.RESET}")
        make_call()
        if i < args.repeat - 1:
            time.sleep(5)

if __name__ == "__main__":
    main()
