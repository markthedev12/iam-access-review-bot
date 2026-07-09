import csv
import json
from datetime import datetime
from pathlib import Path

from src.models import User, Entitlement


def load_role_baseline(path: str) -> dict:
    """Load the role baseline JSON into a Python dict."""
    with open(path, "r") as f:
        return json.load(f)


def load_access_export(path: str) -> list[User]:
    """Load the access export CSV and group rows into User objects."""
    users_by_id: dict[str, User] = {}

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = row["user_id"]

            if user_id not in users_by_id:
                users_by_id[user_id] = User(
                    user_id=user_id,
                    name=row["name"],
                    role=row["role"],
                )

            entitlement = Entitlement(
                system=row["system"],
                group=row["group"],
                last_reviewed=datetime.strptime(row["last_reviewed"], "%Y-%m-%d").date(),
                privileged=row["privileged"].strip().lower() == "true",
            )
            users_by_id[user_id].entitlements.append(entitlement)

    return list(users_by_id.values())