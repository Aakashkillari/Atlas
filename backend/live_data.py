"""Live PMIS statistics from the Government of India Open Data platform.

Source: data.gov.in resource 15362686-dd5c-46e1-aa54-492c5a7d7826
(State/UT-wise candidates who accepted PMIS internship offers, Pilot Round-I,
Rajya Sabha unstarred question 1331, answered 11 March 2025).

Uses the platform's published sample API key by default; set
DATA_GOV_API_KEY for a personal registered key. Responses are cached for
10 minutes; any failure returns None so the UI can fall back gracefully.
"""
import json
import os
import time
import urllib.parse
import urllib.request

RESOURCE_ID = "15362686-dd5c-46e1-aa54-492c5a7d7826"

# Additional PMIS datasets on data.gov.in (all from Parliament replies)
INSIGHT_RESOURCES = {
    "profiles": "0be754b5-f7e5-405b-87ca-6c5c4c9f764a",       # completed profiles 2024-25
    "opportunities": "96478801-1ee3-4c10-9223-08bfc6c5efa6",  # opportunities offered R1
    "offers": "dc168c29-b2c8-433f-9c14-c90de4577fcb",         # offers made R1
    "accepted": "15362686-dd5c-46e1-aa54-492c5a7d7826",       # offers accepted R1
}
# Published public sample key from data.gov.in documentation (not a secret)
SAMPLE_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
CACHE_TTL_SECONDS = 600
TIMEOUT = 12

_cache: dict = {"at": 0.0, "data": None}


def fetch_pmis_stats() -> dict | None:
    now = time.time()
    if _cache["data"] is not None and now - _cache["at"] < CACHE_TTL_SECONDS:
        return _cache["data"]
    try:
        key = os.environ.get("DATA_GOV_API_KEY", SAMPLE_KEY)
        raw = {}
        rows: list[dict] = []
        # the sample key returns at most 10 records per call; paginate
        for offset in range(0, 100, 10):
            url = ("https://api.data.gov.in/resource/" + RESOURCE_ID
                   + "?" + urllib.parse.urlencode(
                       {"api-key": key, "format": "json",
                        "limit": 10, "offset": offset}))
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (ATLAS-SIH25033)",
                "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                raw = json.loads(resp.read())
            page = raw.get("records", [])
            rows.extend(page)
            if not page or len(rows) >= int(raw.get("total", 0) or 0):
                break
        records = []
        for r in rows:
            state = r.get("state_ut") or r.get("state/ut") or r.get("State/UT") or ""
            count_raw = (r.get("number_of_applicants")
                         or r.get("Number of Applicants") or 0)
            try:
                count = int(str(count_raw).replace(",", ""))
            except ValueError:
                continue
            if state and state.strip().lower() not in ("total", "grand total"):
                records.append({"state": state.strip(), "accepted": count})
        records.sort(key=lambda x: -x["accepted"])
        data = {
            "source": "data.gov.in (Open Government Data Platform India)",
            "resource": RESOURCE_ID,
            "title": raw.get("title", "PMIS accepted offers by State/UT"),
            "updated": raw.get("updated_date") or raw.get("updated", ""),
            "total_accepted": sum(r["accepted"] for r in records),
            "records": records,
        }
        _cache.update(at=now, data=data)
        return data
    except Exception:
        return _cache["data"]  # stale cache if available, else None


_insight_cache: dict = {"at": 0.0, "data": None}
INSIGHT_CACHE_TTL = 6 * 3600
SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "data", "pmis_snapshot.json")


def _fetch_resource_rows(resource_id: str, key: str) -> list[dict]:
    rows: list[dict] = []
    for offset in range(0, 100, 10):
        url = ("https://api.data.gov.in/resource/" + resource_id
               + "?" + urllib.parse.urlencode(
                   {"api-key": key, "format": "json", "limit": 10, "offset": offset}))
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (ATLAS-SIH25033)", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = json.loads(resp.read())
        page = raw.get("records", [])
        rows.extend(page)
        if not page or len(rows) >= int(raw.get("total", 0) or 0):
            break
        time.sleep(1.2)  # stay under the sample key's rate limit
    return rows


def _state_and_count(record: dict) -> tuple[str, int] | None:
    state = ""
    count = None
    for k, v in record.items():
        kl = k.lower()
        if kl.startswith("state") or kl in ("ut", "state/ut", "states_uts"):
            state = str(v).strip()
        elif any(w in kl for w in ("number", "count", "total", "applicant",
                                   "opportunit", "offer", "profile", "candidate",
                                   "internship", "youth")):
            try:
                count = int(str(v).replace(",", ""))
            except (ValueError, TypeError):
                continue
    if state and count is not None and state.lower() not in ("total", "grand total"):
        return state, count
    return None


def fetch_insights() -> dict | None:
    """State-wise PMIS funnel merged from four government datasets:
    completed profiles -> opportunities offered -> offers made -> accepted."""
    now = time.time()
    if _insight_cache["data"] is not None and now - _insight_cache["at"] < INSIGHT_CACHE_TTL:
        return _insight_cache["data"]
    try:
        key = os.environ.get("DATA_GOV_API_KEY", SAMPLE_KEY)
        merged: dict[str, dict] = {}
        for metric, rid in INSIGHT_RESOURCES.items():
            for rec in _fetch_resource_rows(rid, key):
                parsed = _state_and_count(rec)
                if parsed:
                    state, count = parsed
                    merged.setdefault(state, {})[metric] = count
            time.sleep(1.2)
        states = []
        for state, m in merged.items():
            opp = m.get("opportunities", 0)
            acc = m.get("accepted", 0)
            offers = m.get("offers", 0)
            profiles = m.get("profiles", 0)
            states.append({
                "state": state,
                "profiles": profiles,
                "opportunities": opp,
                "offers": offers,
                "accepted": acc,
                "acceptance_rate": round(acc / offers, 3) if offers else None,
                "demand_supply_gap": profiles - opp if profiles and opp else None,
            })
        states.sort(key=lambda s: -(s["accepted"] or 0))
        data = {
            "source": "data.gov.in (Open Government Data Platform India)",
            "datasets": INSIGHT_RESOURCES,
            "totals": {
                "profiles": sum(s["profiles"] or 0 for s in states),
                "opportunities": sum(s["opportunities"] or 0 for s in states),
                "offers": sum(s["offers"] or 0 for s in states),
                "accepted": sum(s["accepted"] or 0 for s in states),
            },
            "states": states,
        }
        data["live"] = True
        _insight_cache.update(at=now, data=data)
        try:
            os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
            with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError:
            pass
        return data
    except Exception:
        if _insight_cache["data"] is not None:
            return _insight_cache["data"]
        # fall back to the committed snapshot of the same government data
        try:
            with open(SNAPSHOT_PATH, encoding="utf-8") as f:
                snap = json.load(f)
            snap["live"] = False
            _insight_cache.update(at=now - INSIGHT_CACHE_TTL + 600, data=snap)
            return snap
        except OSError:
            return None
