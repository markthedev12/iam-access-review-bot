from datetime import date

from src.models import User, Flag

STALE_THRESHOLD_DAYS = 90


def review_user(user: User, baseline: dict, today: date | None = None) -> list[Flag]:
    """Compare one user's entitlements against their role baseline and return flags."""
    if today is None:
        today = date.today()

    flags: list[Flag] = []
    role_rules = baseline.get(user.role)

    if role_rules is None:
        flags.append(Flag(
            user_id=user.user_id,
            name=user.name,
            flag_type="excess_access",
            detail=f"Role '{user.role}' not found in baseline — cannot validate access",
            risk_level="medium",
        ))
        return flags

    expected_systems = set(role_rules["expected_systems"])
    expected_groups = set(role_rules["expected_groups"])
    max_privileged = role_rules["max_privileged_access"]

    for ent in user.entitlements:
        if ent.system not in expected_systems or ent.group not in expected_groups:
            flags.append(Flag(
                user_id=user.user_id,
                name=user.name,
                flag_type="excess_access",
                detail=f"Access to '{ent.system}' / '{ent.group}' not expected for role '{user.role}'",
                risk_level="medium",
            ))

        days_since_review = (today - ent.last_reviewed).days
        if days_since_review > STALE_THRESHOLD_DAYS:
            flags.append(Flag(
                user_id=user.user_id,
                name=user.name,
                flag_type="stale_access",
                detail=f"'{ent.system}' access last reviewed {days_since_review} days ago",
                risk_level="low",
            ))

        if ent.privileged and not max_privileged:
            flags.append(Flag(
                user_id=user.user_id,
                name=user.name,
                flag_type="privilege_violation",
                detail=f"Privileged access to '{ent.system}' not permitted for role '{user.role}'",
                risk_level="high",
            ))

    return flags


def review_all_users(users: list[User], baseline: dict) -> list[Flag]:
    """Run review_user across every user and combine all flags."""
    all_flags: list[Flag] = []
    for user in users:
        all_flags.extend(review_user(user, baseline))
    return all_flags