print("STEP 1 - starting safescore engine")

# ── imports ──────────────────────────────────────────────────────────────────
try:
    import os
    import pandas as pd
    from dotenv import load_dotenv
    from colorama import init, Fore, Style
    from supabase import create_client
    print("imports loaded successfully")
except Exception as e:
    print("ERROR during imports: " + str(e))
    raise SystemExit(1)

# ── STEP 2 - load .env ───────────────────────────────────────────────────────
try:
    env_path = "C:/Users/raksh/safemesh-backend/.env"
    load_dotenv(dotenv_path=env_path)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    print("STEP 2 - env loaded")
    print("  SUPABASE_URL: " + str(SUPABASE_URL))
except Exception as e:
    print("ERROR loading .env: " + str(e))
    raise SystemExit(1)

# ── STEP 3 - read CSV ─────────────────────────────────────────────────────────
try:
    csv_path = "C:/Users/raksh/safemesh-backend/data/drivers.csv"
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    print("STEP 3 - csv loaded")
    print("  Rows loaded: " + str(len(df)))
    for i, row in df.iterrows():
        print("  " + str(row["driver_id"]) + " | " + str(row["name"]) + " | hermesh=" + str(row["hermesh_score"]) + " | safesignal=" + str(row["safesignal_score"]) + " | platform=" + str(row["platform_rating"]))
except Exception as e:
    print("ERROR reading CSV: " + str(e))
    raise SystemExit(1)

# ── STEP 4 - compute safescore ────────────────────────────────────────────────
try:
    df["safescore"] = (df["hermesh_score"] * 0.4) + (df["safesignal_score"] * 0.4) + (df["platform_rating"] * 0.2)
    df["safescore"] = df["safescore"].round(1)
    print("STEP 4 - scores computed")
    for i, row in df.iterrows():
        print("  " + str(row["name"]) + " => safescore: " + str(row["safescore"]))
except Exception as e:
    print("ERROR computing safescores: " + str(e))
    raise SystemExit(1)

# ── STEP 5 - assign status ────────────────────────────────────────────────────
try:
    def assign_status(score):
        if score >= 75:
            return "allocated"
        elif score >= 60:
            return "eligible"
        else:
            return "blocked"

    df["status"] = df["safescore"].apply(assign_status)
    print("STEP 5 - status assigned")
    for i, row in df.iterrows():
        print("  " + str(row["name"]) + " => " + str(row["status"]))
except Exception as e:
    print("ERROR assigning status: " + str(e))
    raise SystemExit(1)

# ── sort by safescore descending ──────────────────────────────────────────────
try:
    df = df.sort_values(by="safescore", ascending=False).reset_index(drop=True)
    print("sorted by safescore descending")
except Exception as e:
    print("ERROR sorting dataframe: " + str(e))

# ── print allocation table ────────────────────────────────────────────────────
try:
    init(autoreset=True)
    print("")
    print("===== SAFEMESH DRIVER ALLOCATION TABLE =====")
    for i, row in df.iterrows():
        rank = str(i + 1)
        name = str(row["name"])
        score = str(row["safescore"])
        status = str(row["status"]).upper()

        if row["status"] == "allocated":
            color = Fore.GREEN
        elif row["status"] == "eligible":
            color = Fore.YELLOW
        else:
            color = Fore.RED

        line = rank + ". " + name + " | Score: " + score + " | " + status
        print(color + line + Style.RESET_ALL)
    print("")
except Exception as e:
    print("ERROR printing allocation table: " + str(e))

# ── STEP 6 - connect to Supabase and update drivers table ─────────────────────
try:
    print("STEP 6 - connecting to supabase")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("supabase client created successfully")
except Exception as e:
    print("ERROR connecting to supabase: " + str(e))
    raise SystemExit(1)

try:
    for i, row in df.iterrows():
        try:
            driver_name = str(row["name"])
            safescore_val = float(row["safescore"])
            status_val = str(row["status"])

            response = supabase.table("drivers").update({
                "safescore": safescore_val,
                "status": status_val
            }).eq("name", driver_name).execute()

            print("updated " + driver_name)
        except Exception as e:
            print("ERROR updating " + str(row["name"]) + ": " + str(e))
except Exception as e:
    print("ERROR during supabase update loop: " + str(e))

print("ALL DONE")
