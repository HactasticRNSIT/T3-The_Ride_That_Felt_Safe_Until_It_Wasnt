code = open('safescore.py', 'w')
code.write("""import os
import pandas as pd
from colorama import init, Fore, Style
from dotenv import load_dotenv
from supabase import create_client

init(autoreset=True)
print("starting...")

CSV_PATH = "C:/Users/raksh/safemesh-backend/data/drivers.csv"
ENV_PATH = "C:/Users/raksh/safemesh-backend/.env"

load_dotenv(dotenv_path=ENV_PATH)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

df = pd.read_csv(CSV_PATH)
df["safescore"] = (df["hermesh_score"] * 0.4 + df["safesignal_score"] * 0.4 + df["platform_rating"] * 0.2).round(2)

def assign_status(score):
    if score >= 75: return "allocated"
    elif score >= 60: return "eligible"
    else: return "blocked"

df["status"] = df["safescore"].apply(assign_status)
df.sort_values("safescore", ascending=False, inplace=True)

print()
print("===== SAFEMESH DRIVER ALLOCATION TABLE =====")
print()

for rank, row in enumerate(df.itertuples(), start=1):
    if row.status == "allocated": colour = Fore.GREEN
    elif row.status == "eligible": colour = Fore.YELLOW
    else: colour = Fore.RED
    print(colour + str(rank) + ". " + str(row.driver_id) + " | " + row.name + " | Score: " + str(row.safescore) + " | " + row.status.upper())

print()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
for row in df.itertuples():
    supabase.table("drivers").update({"safescore": row.safescore, "status": row.status}).eq("name", row.name).execute()
    print(Fore.GREEN + "updated " + row.name)

print("ALL DONE")
""")
code.close()
print("file written successfully")