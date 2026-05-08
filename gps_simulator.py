import os
import time
import random
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": FIREBASE_DB_URL
})

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")

BASE_LAT = 12.9716
BASE_LNG = 77.5946

lat = BASE_LAT
lng = BASE_LNG

try:
    for tick in range(1, 21):
        lat += random.uniform(-0.001, 0.001)
        lng += random.uniform(-0.001, 0.001)
        timestamp = datetime.utcnow().isoformat()

        if 1 <= tick <= 7:
            db.reference("/rides/ride_001/passenger_gps").set({
                "lat": lat,
                "lng": lng,
                "timestamp": timestamp
            })
            db.reference("/rides/ride_001/driver_gps").set({
                "lat": lat,
                "lng": lng,
                "timestamp": timestamp
            })
            print(f"STATE → BOTH_ONLINE | Tick {tick} | lat={lat:.4f} lng={lng:.4f}")

        elif tick == 8:
            db.reference("/rides/ride_001/passenger_gps").set({
                "lat": lat,
                "lng": lng,
                "timestamp": timestamp
            })
            print("STATE → DRIVER_OFFLINE | driver GPS stopped")

        elif 9 <= tick <= 13:
            db.reference("/rides/ride_001/passenger_gps").set({
                "lat": lat,
                "lng": lng,
                "timestamp": timestamp
            })
            print(f"STATE → DRIVER_OFFLINE | Tick {tick} | passenger still active")

        elif tick == 14:
            print("STATE → BOTH_OFFLINE | CRITICAL — both signals lost")

        elif tick == 15:
            current_time = datetime.now().strftime("%H:%M")
            sms_body = (
                f"[SafeMesh SOS] Ride anomaly detected. "
                f"Last known location: 12.9716° N, 77.5946° E. "
                f"Time: {current_time}. Contact passenger immediately."
            )
            twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            twilio_client.messages.create(
                body=sms_body,
                from_=TWILIO_FROM_NUMBER,
                to=TWILIO_TO_NUMBER
            )
            print(f"SOS SMS fired to {TWILIO_TO_NUMBER}")

        elif 16 <= tick <= 20:
            print("STATE → BOTH_OFFLINE | awaiting response")

        time.sleep(5)

except KeyboardInterrupt:
    print("Simulator stopped.")