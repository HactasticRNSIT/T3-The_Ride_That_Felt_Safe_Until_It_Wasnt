print("STEP 1 - starting GPS replay")

# ── imports ───────────────────────────────────────────────────────────────────
try:
    import math
    import os
    from dotenv import load_dotenv
    from supabase import create_client
    print("imports loaded successfully")
except Exception as e:
    print("ERROR during imports: " + str(e))
    raise SystemExit(1)

# ── Haversine formula ─────────────────────────────────────────────────────────
def haversine_meters(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ── waypoint definitions ──────────────────────────────────────────────────────
# Route: Bengaluru city centre heading south-east toward Koramangala
# Expected straight-line path used for deviation reference
# Waypoints 7 and 9 are deliberately offset (anomalies)

waypoints = [
    {"n": 1,  "lat": 12.9716, "lon": 77.5946},   # Start - City Centre
    {"n": 2,  "lat": 12.9700, "lon": 77.5960},   # Normal
    {"n": 3,  "lat": 12.9685, "lon": 77.5975},   # Normal
    {"n": 4,  "lat": 12.9670, "lon": 77.5990},   # Normal
    {"n": 5,  "lat": 12.9655, "lon": 77.6005},   # Normal
    {"n": 6,  "lat": 12.9640, "lon": 77.6020},   # Normal
    {"n": 7,  "lat": 12.9660, "lon": 77.6060},   # ANOMALY - offset ~320m east
    {"n": 8,  "lat": 12.9610, "lon": 77.6050},   # Normal
    {"n": 9,  "lat": 12.9570, "lon": 77.6100},   # ANOMALY - offset ~260m north-east
    {"n": 10, "lat": 12.9580, "lon": 77.6080},   # Normal
    {"n": 11, "lat": 12.9565, "lon": 77.6095},   # Normal
    {"n": 12, "lat": 12.9550, "lon": 77.6110},   # End - Koramangala area
]

# Expected path: straight interpolation between start and end
START_LAT = 12.9716
START_LON = 77.5946
END_LAT   = 12.9550
END_LON   = 77.6110
ANOMALY_THRESHOLD = 200  # meters

def expected_position(n, total):
    fraction = (n - 1) / (total - 1)
    lat = START_LAT + fraction * (END_LAT - START_LAT)
    lon = START_LON + fraction * (END_LON - START_LON)
    return lat, lon

# ── walk through waypoints ────────────────────────────────────────────────────
anomaly_detected = False
anomaly_waypoints = []

print("starting waypoint walk...")
print("")

try:
    total = len(waypoints)
    for wp in waypoints:
        n   = wp["n"]
        lat = wp["lat"]
        lon = wp["lon"]

        exp_lat, exp_lon = expected_position(n, total)
        deviation = haversine_meters(lat, lon, exp_lat, exp_lon)
        deviation_rounded = round(deviation, 1)

        print("Waypoint " + str(n) + " - lat: " + str(lat) + ", lng: " + str(lon) + " - checking deviation...")

        if deviation > ANOMALY_THRESHOLD:
            print("ANOMALY DETECTED at waypoint " + str(n) + " - deviation: " + str(deviation_rounded) + "m")
            anomaly_detected = True
            anomaly_waypoints.append(n)
        else:
            print("Waypoint " + str(n) + " - OK")
except Exception as e:
    print("ERROR walking waypoints: " + str(e))

print("")

# ── if anomaly found, write to Supabase ───────────────────────────────────────
if anomaly_detected:
    try:
        print("anomaly found at waypoints: " + str(anomaly_waypoints))
        print("loading .env for supabase connection...")

        env_path = "C:/Users/raksh/safemesh-backend/.env"
        load_dotenv(dotenv_path=env_path)
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        print("env loaded successfully")
    except Exception as e:
        print("ERROR loading .env: " + str(e))
        raise SystemExit(1)

    try:
        print("connecting to supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("supabase client created")
    except Exception as e:
        print("ERROR connecting to supabase: " + str(e))
        raise SystemExit(1)

    try:
        print("writing anomaly flag to rides table for RIDE001...")
        response = supabase.table("rides").update({
            "anomaly_flagged": True
        }).eq("id", 1).execute()
        print("anomaly written to supabase")
        print("response: " + str(response))
    except Exception as e:
        print("ERROR writing anomaly to supabase: " + str(e))
else:
    print("no anomalies detected - supabase update skipped")

print("")
print("GPS REPLAY COMPLETE")
