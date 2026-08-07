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
