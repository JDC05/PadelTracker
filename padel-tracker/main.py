import os
import sys
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
import requests
from flask import Flask

app = Flask(__name__)

API_URL = "https://fastapi-production-fargate.padelmates.io/player/player_booking/all_courts_slot_prices_v2"
CLUB_ID = "788fa2c66535421aabc60fd27f941c42"
LONDON_TZ = ZoneInfo("Europe/London")
UTC_TZ = ZoneInfo("UTC")

def day_bounds_ms(date: datetime) -> tuple[int, int]:
    start = datetime.combine(date.date(), time.min, tzinfo=LONDON_TZ).astimezone(UTC_TZ)
    end = datetime.combine(date.date(), time.max, tzinfo=LONDON_TZ).astimezone(UTC_TZ)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def fetch_slots(start_ms: int, end_ms: int) -> list[dict]:
    params = {"club_id": CLUB_ID, "start_datetime": start_ms, "end_datetime": end_ms}
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("allSlots", [])


def parse_slots(raw_slots: list[dict]) -> list[dict]:
    best: dict[tuple, dict] = {}
    for slot in raw_slots:
        court = slot.get("courtName", "")
        if "meeting room" in court.lower():
            continue
        key = (court, slot["startTimestamp"])
        existing = best.get(key)
        if existing is None or slot.get("duration") == 60:
            best[key] = slot
    return list(best.values())


def ms_to_london(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=UTC_TZ).astimezone(LONDON_TZ)


def build_message(ordered: list[tuple[str, dict[str, list[dict]]]]) -> str:
    if not any(courts for _, courts in ordered):
        return "No available slots in the next 7 days."

    lines = ["**Rocket Padel Ilford — Available Slots**\n"]
    for date_label, courts in ordered:
        if not courts:
            continue
        lines.append(f"**{date_label}**")
        for court_name, slots in sorted(courts.items()):
            lines.append(f"  {court_name}")
            for slot in sorted(slots, key=lambda s: s["startTimestamp"]):
                start = ms_to_london(slot["startTimestamp"])
                end = ms_to_london(slot["endTimestamp"])
                duration = slot.get("duration", "?")
                price = slot.get("price", 0)
                lines.append(f"    {start.strftime('%H:%M')}–{end.strftime('%H:%M')} ({duration}min)  £{price:.2f}")
        lines.append("")
    return "\n".join(lines).rstrip()


def send_discord(message: str) -> None:
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    chunks = []
    current = ""
    for line in message.splitlines(keepends=True):
        if len(current) + len(line) > 1900:
            chunks.append(current.rstrip())
            current = line
        else:
            current += line
    if current:
        chunks.append(current.rstrip())

    for chunk in chunks:
        resp = requests.post(webhook_url, json={"content": chunk}, timeout=10)
        resp.raise_for_status()


def main() -> None:
    now = datetime.now(LONDON_TZ)
    slots_by_day: dict[str, dict[str, list[dict]]] = {}

    for offset in range(7):
        day = now + timedelta(days=offset)
        sort_key = day.strftime("%Y%m%d|%A %-d %B")
        start_ms, end_ms = day_bounds_ms(day)

        try:
            raw = fetch_slots(start_ms, end_ms)
        except requests.RequestException as exc:
            print(f"Warning: failed to fetch {day.strftime('%A %-d %B')}: {exc}", file=sys.stderr)
            slots_by_day[sort_key] = {}
            continue

        deduped = parse_slots(raw)
        courts: dict[str, list[dict]] = {}
        for slot in deduped:
            courts.setdefault(slot["courtName"], []).append(slot)
        slots_by_day[sort_key] = courts

    ordered = [(k.split("|", 1)[1], v) for k, v in sorted(slots_by_day.items())]
    message = build_message(ordered)

    print(message)

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        send_discord(message)
        print("\nSent to Discord.")
    else:
        print("\n(Set DISCORD_WEBHOOK_URL in .env to send to Discord.)", file=sys.stderr)


@app.route("/run", methods=["GET", "POST"])
def run():
    main()
    return "OK", 200

@app.route("/", methods=["GET"])
def health():
    return "padel-tracker running", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
