from datetime import date
from events import get_event_name, get_roster_format

NUMBERS = ["❶", "❷", "❸", "❹", "❺", "❻", "❼", "❽"]


def _num(i: int) -> str:
    return NUMBERS[i] if i < len(NUMBERS) else f"**{i + 1}.**"


def format_event_results(
    players_data: list[tuple[str, list[dict] | None]],
    report_date: date | None = None,
) -> list[str]:
    """
    players_data: [(epic_id, events_list), ...]
    大会コード別にまとめてDiscord送信用メッセージリストを返す
    """
    # 大会コードごとに { epic_id: event_data } を作る
    all_codes: dict[str, dict] = {}
    for epic_id, events in players_data:
        if not events:
            continue
        for ev in events:
            code = ev["code"]
            if code not in all_codes:
                all_codes[code] = {}
            all_codes[code][epic_id] = ev

    if not all_codes:
        return []

    # 日付文字列
    if report_date is None:
        all_dates = [
            ev["last_modified_date"]
            for _, events in players_data if events
            for ev in events if ev.get("last_modified_date")
        ]
        report_date = max(all_dates) if all_dates else date.today()

    date_str = report_date.strftime("%Y/%m/%d")

    messages = []
    for code, player_map in all_codes.items():
        event_name = get_event_name(code)
        roster_fmt = get_roster_format(code)
        lines = [f"🏆 **{event_name}**　📅 {date_str}\n"]

        for i, (epic_id, _) in enumerate(players_data):
            ev = player_map.get(epic_id)
            if not ev:
                continue

            kd = round(ev["kills"] / max(ev["matches"] - ev["wins"], 1), 2)
            score = ev["score"]

            # プレースメント内訳を組み立てる
            placement_parts = []
            if ev["wins"] > 0:
                placement_parts.append(f"🥇{ev['wins']}")
            top3_excl = ev["top3"] - ev["wins"]
            if top3_excl > 0:
                placement_parts.append(f"Top3: {top3_excl}")
            top5_excl = ev["top5"] - ev["top3"]
            if top5_excl > 0:
                placement_parts.append(f"Top5: {top5_excl}")
            top10_excl = ev["top10"] - ev["top5"]
            if top10_excl > 0:
                placement_parts.append(f"Top10: {top10_excl}")
            top12_excl = ev["top12"] - ev["top10"]
            if top12_excl > 0:
                placement_parts.append(f"Top12: {top12_excl}")
            placement_str = "　".join(placement_parts) if placement_parts else "—"

            lines.append(
                f"{_num(i)} **{epic_id}** ・ Score: `{score:,}`\n"
                f"Roster: {roster_fmt}\n"
                f"Matches: {ev['matches']}　Wins: {ev['wins']}　Elims: {ev['kills']}\n"
                f"Placement: {placement_str}\n"
                f"K/D: {kd}\n"
                f"＝＝＝"
            )

        if len(lines) > 1:
            messages.append("\n".join(lines))

    return messages
