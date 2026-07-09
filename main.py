from src.loader import load_role_baseline, load_access_export
from src.review_engine import review_all_users
from src.report_generator import generate_report


def main():
    print("Loading role baseline...")
    baseline = load_role_baseline("data/role_baseline.json")

    print("Loading access export...")
    users = load_access_export("data/access_export.csv")
    print(f"Loaded {len(users)} users")

    print("Running access review...")
    flags = review_all_users(users, baseline)
    print(f"Found {len(flags)} flags")

    print("Generating report...")
    generate_report(flags, total_users=len(users), output_path="access_review_report.html")

    print("Done. Report saved to access_review_report.html")


if __name__ == "__main__":
    main()