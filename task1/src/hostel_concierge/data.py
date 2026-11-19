"""Read-only access to the hostel's mock data."""

import json
from datetime import datetime, time
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class GuestNotFoundError(LookupError):
    """Raised when the app-provided guest identity is not in the mock data."""


def load_guests() -> list[dict[str, Any]]:
    with (DATA_DIR / "guests.json").open(encoding="utf-8") as guests_file:
        return json.load(guests_file)


def get_guest(guest_id: str) -> dict[str, Any]:
    for guest in load_guests():
        if guest["guest_id"] == guest_id:
            return guest
    raise GuestNotFoundError(f"No booking was found for guest {guest_id!r}.")


def get_kitchen_info(now: datetime | None = None) -> dict[str, Any]:
    with (DATA_DIR / "kitchen.json").open(encoding="utf-8") as kitchen_file:
        kitchen = json.load(kitchen_file)

    current_time = (now or datetime.now()).time().replace(tzinfo=None)
    is_open = any(
        time.fromisoformat(hours["opens"])
        <= current_time
        < time.fromisoformat(hours["closes"])
        for hours in kitchen["kitchen_hours"].values()
    )
    return {
        "is_open": is_open,
        "kitchen_hours": kitchen["kitchen_hours"],
        "menu": kitchen["menu"],
    }