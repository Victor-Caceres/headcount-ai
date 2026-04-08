import os
import anthropic
from dotenv import load_dotenv

from db import get_model_data
from formulas import (
    effective_capacity,
    tickets_handleable,
    agents_required,
    utilization_actual,
    staffing_gap,
    regional_summary,
)
from tools import TOOLS

load_dotenv()

_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

_FORMULA_DISPATCH = {
    "effective_capacity": effective_capacity,
    "tickets_handleable": tickets_handleable,
    "agents_required": agents_required,
    "utilization_actual": utilization_actual,
    "staffing_gap": staffing_gap,
}


def _format_model_data(data: dict) -> str:
    ga = data["global_assumptions"]
    roster = data["roster"]
    tickets = data["projected_tickets"]

    lines = [
        "Global Assumptions:",
        f"- Working hours per month: {ga['working_hours_per_month']}",
        f"- Shrinkage rate: {ga['shrinkage_rate'] * 100:.0f}%",
        f"- Utilization target: {ga['utilization_target'] * 100:.0f}%",
        "",
        "Roster:",
    ]
    for region, info in roster.items():
        lines.append(f"- {region}: {info['agents']} agents, {info['aht_minutes']} min AHT")

    lines += ["", "Projected Ticket Volume:"]
    for region, vol in tickets.items():
        lines.append(f"- {region}: {vol:,}")

    return "\n".join(lines)


def _call_tool(name: str, inputs: dict, model_data: dict):
    if name == "regional_summary":
        ga = model_data["global_assumptions"]
        return regional_summary(
            roster=model_data["roster"],
            projected_tickets=model_data["projected_tickets"],
            working_hours=ga["working_hours_per_month"],
            shrinkage_rate=ga["shrinkage_rate"],
            utilization_target=ga["utilization_target"],
        )
    return _FORMULA_DISPATCH[name](**inputs)


def run_agent(message: str) -> dict:
    model_data = get_model_data()

    system_prompt = (
        "You are a headcount planning assistant for a global support "
        "operations team. You have access to tools that perform workforce "
        "calculations.\n\n"
        "RULES — follow these without exception:\n"
        "1. You are a router and composer only. Never perform arithmetic "
        "yourself. Extract parameters from the question, call the "
        "appropriate tool, and compose your answer exclusively from "
        "the values returned by that tool.\n"
        "2. Every number in your response must come from a tool return "
        "value. Show intermediate values so the math is fully auditable.\n"
        "3. If a question requires data not in this model — such as costs, "
        "attrition rates, ramp time, or historical trends — respond with "
        "exactly: 'That question requires data not currently in this "
        "model.' Do not estimate or approximate.\n"
        "4. For questions involving relative changes (e.g. 'increases by "
        "30%', 'adds 2 minutes'), resolve the absolute parameter value "
        "from the current model data before calling the tool.\n\n"
        "CURRENT MODEL DATA:\n"
        + _format_model_data(model_data)
    )

    messages = [{"role": "user", "content": message}]
    tools_called = []

    while True:
        response = _client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            answer = next(
                (block.text for block in response.content if hasattr(block, "text")),
                "",
            )
            return {"answer": answer, "tools_called": tools_called}

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tools_called.append(block.name)
                    result = _call_tool(block.name, block.input, model_data)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
