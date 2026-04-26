# 🎾 Padel Court Availability Tracker

A daily automated notifier that tracks free court slots at **Rocket Padel Ilford** and delivers them straight to a Discord channel — so me and my friends never miss a booking again.

## Why I Built This

Court slots at Rocket Padel Ilford fill up fast. My friends and I kept missing available times because we'd check the PadelMates app too late. Rather than refreshing the app manually every day, I built this tool to automatically fetch all free slots across all 11 courts for the next 7 days and post them to our Discord server every morning at 8am — so the whole group can plan and book before slots disappear.

## How It Works

1. A **Cloud Scheduler** job triggers daily at 8am (Europe/London)
2. It hits a **Cloud Run** service running a Python Flask app
3. The app calls the **PadelMates API** to fetch all available slots across 11 courts for the next 7 days
4. Results are formatted and posted to a **Discord webhook** — visible to everyone in the group

## Example Output

```
🎾 Rocket Padel Ilford — Available Slots

**Tuesday 29 April**
  1. A.S.K Lettings
    07:00–08:00 (60min)  £40.00
  5. GoOfficial Travel
    09:00–10:00 (60min)  £22.00
    11:00–12:00 (60min)  £22.00
  7. CUPRA Court
    13:30–15:00 (90min)  £60.00
...
```

## Tech Stack

- **Python 3.11** — core script
- **Flask** — lightweight HTTP wrapper for Cloud Run
- **Docker** — containerised for consistent deployment
- **GCP Cloud Run** — serverless hosting (scales to zero when not in use)
- **GCP Cloud Build** — CI/CD pipeline triggered on every GitHub push
- **GCP Cloud Scheduler** — cron job triggering daily execution
- **Discord Webhook** — delivers results to a shared group channel

## Architecture

```
GitHub push
    │
    ▼
Cloud Build (CI/CD)
    │  builds Docker image
    ▼
Cloud Run (Flask app)
    ▲
    │  HTTP POST /run daily at 08:00
Cloud Scheduler
```

## Setup & Deployment

### Prerequisites
- GCP account with Cloud Run, Cloud Build, and Cloud Scheduler APIs enabled
- Discord server with a webhook URL
- Docker installed locally (for testing)

### Local Development

```bash
# Clone the repo
git clone https://github.com/JDC05/padel-tracker.git
cd padel-tracker

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DISCORD_WEBHOOK_URL=your_webhook_url_here

# Run locally
python main.py
```

### Cloud Deployment

Deployment is fully automated via Cloud Build. Any push to `main` triggers a new build and deploys to Cloud Run automatically.

Environment variables (e.g. `DISCORD_WEBHOOK_URL`) are configured directly on the Cloud Run service — no secrets are stored in the repository.

## Configuration

| Variable | Description |
|---|---|
| `DISCORD_WEBHOOK_URL` | Discord webhook URL to post slot availability to |

The club ID and API endpoint are hardcoded for Rocket Padel Ilford. To adapt for a different PadelMates club, update `CLUB_ID` in `main.py`.

## Project Structure

```
padel-tracker/
├── main.py           # Core logic — API fetch, parsing, Discord notification
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container configuration
└── README.md
```
