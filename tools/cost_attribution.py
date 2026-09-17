"""Aggregate agent-workload cost events by tenant, project, and run.

The tool intentionally keeps pricing as input so platform teams can align it with
their cloud contracts and model providers instead of baking in fictional rates.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class UnitPrices:
    cpu_second: Decimal = Decimal("0.000011")
    memory_gib_second: Decimal = Decimal("0.0000015")
    input_token: Decimal = Decimal("0.00000015")
    output_token: Decimal = Decimal("0.00000060")


def event_cost(event: dict, prices: UnitPrices = UnitPrices()) -> Decimal:
    """Calculate one run's cost; absent dimensions are safely treated as zero."""
    return (
        Decimal(str(event.get("cpu_seconds", 0))) * prices.cpu_second
        + Decimal(str(event.get("memory_gib_seconds", 0))) * prices.memory_gib_second
        + Decimal(str(event.get("input_tokens", 0))) * prices.input_token
        + Decimal(str(event.get("output_tokens", 0))) * prices.output_token
    )


def aggregate(events: Iterable[dict], prices: UnitPrices = UnitPrices()) -> dict[str, str]:
    """Return exact decimal totals keyed by tenant/project/run."""
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for event in events:
        required = ("tenant_id", "project_id", "agent_run_id")
        missing = [field for field in required if not event.get(field)]
        if missing:
            raise ValueError(f"Missing required attribution fields: {', '.join(missing)}")
        key = "/".join(event[field] for field in required)
        totals[key] += event_cost(event, prices)
    return {key: f"{total:.8f}" for key, total in sorted(totals.items())}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: cost_attribution.py <events.json>", file=sys.stderr)
        return 2
    events = json.loads(Path(argv[1]).read_text())
    if not isinstance(events, list):
        raise ValueError("Expected a JSON array of events")
    print(json.dumps(aggregate(events), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
