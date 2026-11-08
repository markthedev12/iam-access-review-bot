"""Validate untrusted sample exports before constructing review models."""
import csv
import json
from datetime import date
from src.models import User, Entitlement

FIELDS = {"user_id", "name", "role", "system", "group", "last_reviewed", "privileged"}

def load_role_baseline(path):
    with open(path, encoding="utf-8-sig") as file:
        baseline = json.load(file)
    if not isinstance(baseline, dict):
        raise ValueError("baseline must be an object keyed by role")
    for role, rules in baseline.items():
        if not role.strip() or not isinstance(rules, dict):
            raise ValueError("each role must have a rule object")
        for key in ("expected_systems", "expected_groups"):
            value = rules.get(key)
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                raise ValueError(f"{role}: {key} must be a list of non-empty strings")
        if not isinstance(rules.get("max_privileged_access"), bool):
            raise ValueError(f"{role}: max_privileged_access must be a JSON boolean")
    return baseline

def load_access_export(path):
    users = {}
    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        if FIELDS - set(headers) or len(headers) != len(set(headers)):
            raise ValueError("CSV requires unique headers: " + ", ".join(sorted(FIELDS)))
        for line, raw in enumerate(reader, 2):
            if None in raw or any(raw.get(key) is None or not raw[key].strip() for key in FIELDS):
                raise ValueError(f"CSV row {line}: missing values or extra columns")
            row = {key: raw[key].strip() for key in FIELDS}
            if row["privileged"].lower() not in ("true", "false"):
                raise ValueError(f"CSV row {line}: privileged must be true or false")
            try:
                reviewed = date.fromisoformat(row["last_reviewed"])
                if reviewed.isoformat() != row["last_reviewed"]:
                    raise ValueError("non-canonical date")
            except ValueError as error:
                raise ValueError(f"CSV row {line}: last_reviewed must be YYYY-MM-DD") from error
            user_id = row["user_id"]
            user = users.setdefault(user_id, User(user_id, row["name"], row["role"]))
            if user.name != row["name"] or user.role != row["role"]:
                raise ValueError(f"CSV row {line}: conflicting name or role for {user_id}")
            user.entitlements.append(Entitlement(row["system"], row["group"], reviewed,
                                                row["privileged"].lower() == "true"))
    return list(users.values())
