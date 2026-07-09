from dataclasses import dataclass, field
from datetime import date
from typing import Literal

@dataclass
class Entitlement:
    system: str
    group: str
    last_reviewed: date
    privileged: bool

@dataclass
class User:
    user_id: str
    name: str
    role: str
    entitlements: list[Entitlement] = field(default_factory=list)

@dataclass
class Flag:
    user_id: str
    name: str
    flag_type: Literal["excess_access", "stale_access", "privilege_violation"]
    detail: str
    risk_level: Literal["low", "medium", "high"]