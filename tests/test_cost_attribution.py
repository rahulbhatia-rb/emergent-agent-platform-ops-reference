import unittest
from decimal import Decimal

from tools.cost_attribution import UnitPrices, aggregate, event_cost


class CostAttributionTest(unittest.TestCase):
    def setUp(self):
        self.prices = UnitPrices(
            cpu_second=Decimal("1"),
            memory_gib_second=Decimal("2"),
            input_token=Decimal("0.1"),
            output_token=Decimal("0.2"),
        )

    def test_cost_includes_all_dimensions(self):
        event = {"cpu_seconds": 3, "memory_gib_seconds": 4, "input_tokens": 5, "output_tokens": 6}
        self.assertEqual(event_cost(event, self.prices), Decimal("12.7"))

    def test_aggregate_groups_by_attribution_key(self):
        events = [
            {"tenant_id": "a", "project_id": "p", "agent_run_id": "r", "cpu_seconds": 1},
            {"tenant_id": "a", "project_id": "p", "agent_run_id": "r", "cpu_seconds": 2},
        ]
        self.assertEqual(aggregate(events, self.prices), {"a/p/r": "3.00000000"})

    def test_missing_attribution_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "project_id"):
            aggregate([{"tenant_id": "a", "agent_run_id": "r"}], self.prices)


if __name__ == "__main__":
    unittest.main()
