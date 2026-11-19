import unittest
from datetime import datetime

from hostel_concierge.data import GuestNotFoundError, get_guest, get_kitchen_info
from hostel_concierge.services import (
    BookingActionError,
    KitchenClosedError,
    OutOfStockError,
    prepare_booking_action,
    prepare_order,
)


class DataAccessTests(unittest.TestCase):
    def test_guest_lookup_uses_guest_id(self) -> None:
        guest = get_guest("guest-305")

        self.assertEqual(guest["room"], "305")
        self.assertEqual(guest["status"], "checked-in")

    def test_unknown_guest_has_clear_error(self) -> None:
        with self.assertRaises(GuestNotFoundError):
            get_guest("unknown-guest")

    def test_kitchen_is_open_at_opening_time(self) -> None:
        kitchen = get_kitchen_info(datetime(2026, 11, 19, 6, 0))

        self.assertTrue(kitchen["is_open"])
        self.assertEqual(len(kitchen["menu"]), 7)

    def test_kitchen_is_closed_at_closing_time(self) -> None:
        kitchen = get_kitchen_info(datetime(2026, 11, 19, 10, 30))

        self.assertFalse(kitchen["is_open"])

    def test_checkout_returns_pending_approval_for_own_room(self) -> None:
        proposal = prepare_booking_action("guest-305", "check-out")

        self.assertEqual(proposal["room"], "305")
        self.assertEqual(proposal["proposed_status"], "checked-out")
        self.assertTrue(proposal["approval_required"])

    def test_checkin_is_refused_before_booking_date(self) -> None:
        with self.assertRaises(BookingActionError):
            prepare_booking_action("guest-112", "check-in", today=datetime(2026, 11, 19).date())

    def test_order_is_bound_to_guest_room_and_requires_approval(self) -> None:
        order = prepare_order(
            "guest-305",
            [{"item_id": "veg-sandwich", "quantity": 1}, {"item_id": "coffee", "quantity": 2}],
            datetime(2026, 11, 19, 8, 0),
        )

        self.assertEqual(order["room"], "305")
        self.assertEqual(order["total"], 14.5)
        self.assertTrue(order["approval_required"])

    def test_order_is_refused_when_kitchen_is_closed(self) -> None:
        with self.assertRaises(KitchenClosedError):
            prepare_order(
                "guest-305",
                [{"item_id": "coffee", "quantity": 1}],
                datetime(2026, 11, 19, 11, 0),
            )

    def test_order_is_refused_when_item_is_out_of_stock(self) -> None:
        with self.assertRaises(OutOfStockError):
            prepare_order(
                "guest-305",
                [{"item_id": "tomato-soup", "quantity": 1}],
                datetime(2026, 11, 19, 8, 0),
            )


if __name__ == "__main__":
    unittest.main()