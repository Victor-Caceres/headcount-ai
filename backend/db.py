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

_ALL_TABLES = {"global_assumptions", "roster", "projected_tickets"}


def _fetch(table: str) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def _resolve(param, all_sentinel) -> set | None:
    """Return None (fetch all) or a set of values to include."""
    if not param or param == [all_sentinel]:
        return None
    return set(param)


def get_model_data(regions=None, tables=None) -> dict:
    active_regions = _resolve(regions, "ALL")
    active_tables = _resolve(tables, "ALL")

    # global_assumptions is always fetched
    tables_to_fetch = _ALL_TABLES if active_tables is None else (active_tables | {"global_assumptions"})

    result = {}

    if "global_assumptions" in tables_to_fetch:
        raw_global = _fetch("global_assumptions")
        result["global_assumptions"] = {row["key"]: row["value"] for row in raw_global}

    if "roster" in tables_to_fetch:
        raw_roster = _fetch("roster")
        result["roster"] = {
            row["region"]: {
                "agents": row["agents"],
                "aht_minutes": row["aht_minutes"],
            }
            for row in raw_roster
            if active_regions is None or row["region"] in active_regions
        }

    if "projected_tickets" in tables_to_fetch:
        raw_tickets = _fetch("projected_tickets")
        result["projected_tickets"] = {
            row["region"]: row["tickets"]
            for row in raw_tickets
            if active_regions is None or row["region"] in active_regions
        }

    return result
