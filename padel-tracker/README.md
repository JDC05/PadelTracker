# padel-tracker

Checks available court slots at Rocket Padel Ilford for the next 7 days and prints results. Optionally posts them to a Discord channel via webhook.

## Requirements

- Python 3.9+

## Setup

```bash
git clone <repo-url>
cd padel-tracker
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Discord (optional)

1. In Discord: right-click your channel → **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook** → copy the URL
2. Create a `.env` file:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

If `.env` is absent or the variable is unset, the script just prints to stdout.

## Run

```bash
python tracker.py
```

## Cron job

To run every morning at 08:00 London time:

```cron
0 8 * * * cd /path/to/padel-tracker && /path/to/.venv/bin/python tracker.py >> /tmp/padel-tracker.log 2>&1
```
