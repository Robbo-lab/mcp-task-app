"""Reusable MCP resources for the unit converter tutorial."""

from __future__ import annotations

from typing import Any

from app.utils.resource_definition import ResourceDefinition


def unit_reference() -> dict[str, Any]:
    """
    JSON cheatsheet of supported conversions, formulas, and sample IO.

    Returns:
        Dictionary describing conversions, formulas, and examples.
    """
    return {
        "id": "unit-converter-cheatsheet",
        "title": "Unit Converter Cheatsheet",
        "supported": {
            "distance": {
                "miles_to_kilometers": {
                    "formula": "mi ÷ 0.621371",
                    "example": {"input": 3.1, "output": 4.98895},
                },
            },
        },
        "notes": [
            "Negative distances are rejected to keep results meaningful.",
        ],
    }


RESOURCE_DEFINITIONS = [
    ResourceDefinition(
        name="unit_reference",
        display_name="Unit Converter Cheatsheet",
        description="JSON cheatsheet covering formulas and sample conversions.",
        mime_type="application/json",
        func=unit_reference,
    ),
]
