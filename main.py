"""Review a validated access export; findings are human-review prompts."""
import argparse
from datetime import date
from pathlib import Path
from src.loader import load_role_baseline, load_access_export
from src.review_engine import review_all_users
from src.report_generator import generate_report

ROOT = Path(__file__).resolve().parent

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=ROOT / "data/access_export.csv")
    parser.add_argument("--baseline", default=ROOT / "data/role_baseline.json")
    parser.add_argument("--output", default="access_review_report.html")
    parser.add_argument("--as-of", type=date.fromisoformat, default=None)
    args = parser.parse_args(argv)
    try:
        baseline = load_role_baseline(args.baseline)
        users = load_access_export(args.input)
        flags = review_all_users(users, baseline, today=args.as_of)
        generate_report(flags, len(users), args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Review could not complete: {error}\n")
    print(f"Reviewed {len(users)} users; {len(flags)} findings. Report: {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
