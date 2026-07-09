# IAM Access Review Bot

Automated access certification tool that flags excess, stale, and privileged access against defined role baselines mirroring the logic behind SailPoint IdentityNow entitlement review campaigns.

## The Problem

Manual access certification reviews are slow, inconsistent, and easy to get wrong at scale. IAM teams need a repeatable way to answer: *does this person's access still match what their role should have?* This tool automates that comparison and produces a certification ready report.

## What It Does

Given a role baseline (what access each role *should* have) and an access export (what access users *actually* have), the tool flags three types of issues:

- **Excess access** — a system or group not expected for the user's role
- **Stale access** — entitlements not reviewed in over 90 days
- **Privilege violation** — privileged access granted to a role that shouldn't have it

Each flag is risk-scored (low/medium/high) with a recommended action (re-certify, escalate, or revoke immediately), and the results are compiled into an HTML report.

## Example Output

![Access Review Report](docs/report_screenshot.png)

## Tech Stack

- Python 3.14
- pandas — data handling
- Jinja2 — HTML report templating

## How to Run

```bash
git clone https://github.com/markthedev12/iam-access-review-bot.git
cd iam-access-review-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Output is saved to `access_review_report.html` in the project root.

## Project Structure

├── data/                  # Sample role baseline + access export
├── src/
│   ├── models.py          # Core data classes (User, Entitlement, Flag)
│   ├── loader.py          # CSV/JSON ingestion
│   ├── review_engine.py   # Flagging logic
│   └── report_generator.py # HTML report rendering
├── templates/              # Jinja2 report template
├── tests/                  # Unit tests
└── main.py                 # Entry point

## Why I Built This

IAM governance is the part of security that doesn't get talked about enough. It's not flashy, but it's where the real risk lives. Every breach post-mortem eventually traces back to someone having access they shouldn't have had. I wanted to understand that problem from the inside, not just read about it, so I built the tool that actually does the work: comparing real access against what access should look like, and surfacing the gap.

This project came out of studying for CompTIA CySA+ and going deeper on SailPoint IdentityNow concepts. I wanted something that forced me to think through entitlement review logic end to end instead of just memorizing exam material. Working around SailPoint and Entra ID daily gave me the instinct for what a real access review actually needs to catch; building this was about proving I could translate that into a working project.

