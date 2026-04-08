import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
}


def _fetch(table: str) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_model_data() -> dict:
    raw_global = _fetch("global_assumptions")
    raw_roster = _fetch("roster")
    raw_tickets = _fetch("projected_tickets")

    global_assumptions = {row["key"]: row["value"] for row in raw_global}

    roster = {
        row["region"]: {
            "agents": row["agents"],
            "aht_minutes": row["aht_minutes"],
        }
        for row in raw_roster
    }

    projected_tickets = {row["region"]: row["tickets"] for row in raw_tickets}

    return {
        "global_assumptions": global_assumptions,
        "roster": roster,
        "projected_tickets": projected_tickets,
    }
