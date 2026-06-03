import requests
import urllib.parse
import os
import re
from datetime import datetime, timezone, date

BASE_URL = "https://prod.api-fortnite.com"
TOURNAMENT_KEYWORD = "showdowntournament"


def _headers() -> dict:
    api_key = os.getenv("FORTNITE_API_KEY", "").strip()
    return {"x-api-key": api_key, "Accept": "application/json"}


def resolve_account_id(display_name: str) -> str | None:
    try:
        encoded = urllib.parse.quote(display_name)
        r = requests.get(
            f"{BASE_URL}/api/v1/account/displayName/{encoded}",
            headers=_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("id")
        print(f"account lookup failed for {display_name}: {r.status_code}")
        return None
    except Exception as e:
        print(f"account lookup error for {display_name}: {e}")
        return None


def fetch_events(epic_id: str, target_date: date | None = None) -> list[dict] | None:
    """
    大会ごとの統計を返す。
    target_date が指定された場合はその日のイベントのみ返す。
    Noneの場合は最新日のイベントのみ返す。
    """
    try:
        account_id = resolve_account_id(epic_id)
        if not account_id:
            return None

        r = requests.get(
            f"{BASE_URL}/api/v2/stats/{account_id}",
            headers=_headers(),
            timeout=10,
        )
        if r.status_code != 200:
            print(f"stats fetch failed for {epic_id}: {r.status_code}")
            return None

        raw = r.json().get("stats", {})

        # イベントコードごとにステータスを集計
        events: dict[str, dict] = {}
        for key, value in raw.items():
            if TOURNAMENT_KEYWORD not in key:
                continue
            m = re.search(r"playlist_(.+)$", key)
            if not m:
                continue
            event_code = m.group(1)

            if event_code not in events:
                events[event_code] = {
                    "code": event_code,
                    "matches": 0,
                    "wins": 0,
                    "kills": 0,
                    "score": 0,
                    "top3": 0,
                    "top5": 0,
                    "top10": 0,
                    "top12": 0,
                    "last_modified_ts": 0,
                    "last_modified_date": None,
                }

            # メトリクスを解析
            metric = key.split("_keyboardmouse")[0].replace("br_", "").replace("arena_", "")

            if "lastmodified" in metric:
                if isinstance(value, int) and value > events[event_code]["last_modified_ts"]:
                    events[event_code]["last_modified_ts"] = value
                    events[event_code]["last_modified_date"] = datetime.fromtimestamp(
                        value, tz=timezone.utc
                    ).date()
            elif "matchesplayed" in metric:
                events[event_code]["matches"] = max(events[event_code]["matches"], value)
            elif metric == "placetop1":
                events[event_code]["wins"] = max(events[event_code]["wins"], value)
            elif metric == "kills":
                events[event_code]["kills"] = max(events[event_code]["kills"], value)
            elif metric == "score":
                events[event_code]["score"] = max(events[event_code]["score"], value)
            elif "placetop3" in metric:
                events[event_code]["top3"] = max(events[event_code]["top3"], value)
            elif "placetop5" in metric:
                events[event_code]["top5"] = max(events[event_code]["top5"], value)
            elif "placetop10" in metric:
                events[event_code]["top10"] = max(events[event_code]["top10"], value)
            elif "placetop12" in metric:
                events[event_code]["top12"] = max(events[event_code]["top12"], value)

        # 試合数が1以上のイベントだけ対象
        valid = [e for e in events.values() if e["matches"] > 0 and e["last_modified_ts"] > 0]

        if not valid:
            return []

        # フィルタリング対象日を決定
        if target_date is None:
            # 最新日を自動で選ぶ
            latest = max(e["last_modified_date"] for e in valid if e["last_modified_date"])
            filter_date = latest
        else:
            filter_date = target_date

        # 対象日のイベントに絞る
        filtered = [e for e in valid if e["last_modified_date"] == filter_date]
        filtered.sort(key=lambda x: x["last_modified_ts"], reverse=True)

        print(f"[{epic_id}] filter_date={filter_date}, events found={len(filtered)}")
        return filtered

    except Exception as e:
        print(f"fetch_events error for {epic_id}: {e}")
        return None
