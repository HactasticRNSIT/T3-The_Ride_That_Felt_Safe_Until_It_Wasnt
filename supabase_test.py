print("STEP 1 - testing supabase connection")

# ── imports ───────────────────────────────────────────────────────────────────
try:
    import os
    from dotenv import load_dotenv
    from supabase import create_client
    print("imports loaded successfully")
except Exception as e:
    print("ERROR during imports: " + str(e))
    raise SystemExit(1)

# ── load .env and connect ─────────────────────────────────────────────────────
try:
    env_path = "C:/Users/raksh/safemesh-backend/.env"
    load_dotenv(dotenv_path=env_path)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    print("env loaded - URL: " + str(SUPABASE_URL))
except Exception as e:
    print("ERROR loading .env: " + str(e))
    raise SystemExit(1)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("supabase client created successfully")
except Exception as e:
    print("ERROR creating supabase client: " + str(e))
    raise SystemExit(1)

# ── STEP 2 - insert dummy driver ──────────────────────────────────────────────
try:
    dummy = {
        "name": "Test Driver",
        "hermesh_score": 70,
        "safesignal_score": 75,
        "platform_rating": 80,
        "safescore": 74.0,
        "status": "eligible"
    }
    print("inserting dummy driver: " + str(dummy))
    response = supabase.table("drivers").insert(dummy).execute()
    print("STEP 2 - dummy driver inserted")
    print("insert response: " + str(response))
except Exception as e:
    print("ERROR inserting dummy driver: " + str(e))

# ── STEP 3 - query allocated drivers ─────────────────────────────────────────
try:
    print("")
    print("querying allocated drivers...")
    response = supabase.table("drivers").select("*").eq("status", "allocated").execute()
    allocated = response.data
    print("STEP 3 - allocated drivers:")
    if len(allocated) == 0:
        print("  (none found)")
    else:
        for d in allocated:
            print("  name: " + str(d.get("name")) + " | safescore: " + str(d.get("safescore")) + " | status: " + str(d.get("status")))
except Exception as e:
    print("ERROR querying allocated drivers: " + str(e))

# ── STEP 4 - query blocked drivers ───────────────────────────────────────────
try:
    print("")
    print("querying blocked drivers...")
    response = supabase.table("drivers").select("*").eq("status", "blocked").execute()
    blocked = response.data
    print("STEP 4 - blocked drivers:")
    if len(blocked) == 0:
        print("  (none found)")
    else:
        for d in blocked:
            print("  name: " + str(d.get("name")) + " | safescore: " + str(d.get("safescore")) + " | status: " + str(d.get("status")))
except Exception as e:
    print("ERROR querying blocked drivers: " + str(e))

print("")
print("SUPABASE TEST COMPLETE")
