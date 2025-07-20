"""Site Scaffold Agent

Creates essential pages and categories for a new WordPress site.
This is a simplified stub that demonstrates the expected I/O
contract for the agent.
"""

from typing import Any, Dict, List

from ..shared.utils import format_agent_response

AGENT_NAME = "site-scaffold-agent"


def validate(input_data: Dict[str, Any]) -> bool:
    """Validate input for the scaffold agent."""
    if "plan_id" not in input_data:
        raise ValueError("'plan_id' is required")
    return True


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the site scaffold agent."""
    try:
        validate(input_data)
        categories: List[str] = input_data.get("categories", [])

        output = {
            "scaffold": {
                "plan_id": input_data["plan_id"],
                "categories_created": categories,
            }
        }
        return format_agent_response(AGENT_NAME, output)
    except Exception as exc:  # pragma: no cover - protective wrapper
        return format_agent_response(
            AGENT_NAME, {}, status="error", errors=[f"SCAFFOLD_FAIL: {exc}"]
        )
