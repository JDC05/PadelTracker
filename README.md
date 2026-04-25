# padel-tracker

Checks available court slots at Rocket Padel Ilford for the next 7 days and sends a formatted summary to WhatsApp via Twilio.

## Requirements

- Python 3.9+

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd padel-tracker
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run

```bash
# Fetch slots and send WhatsApp message
python tracker.py

# Fetch slots and print only (no WhatsApp send)
python tracker.py --no-send
```

## Output format

```
Rocket Padel Ilford — Available Slots

Saturday 26 April
  Court 1
    09:00–10:00  £18.00
    10:00–11:00  £20.00
  Court 2
    14:00–15:00  £20.00

Sunday 27 April
  ...
```
