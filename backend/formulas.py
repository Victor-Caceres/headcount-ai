import math


def effective_capacity(agents, working_hours, shrinkage_rate, utilization_target):
    effective_hours_per_agent = working_hours * (1 - shrinkage_rate) * utilization_target
    total_capacity_hours = agents * effective_hours_per_agent
    return {
        "effective_hours_per_agent": round(effective_hours_per_agent, 2),
        "total_capacity_hours": round(total_capacity_hours, 2),
    }


def tickets_handleable(agents, aht_minutes, working_hours, shrinkage_rate, utilization_target):
    effective_hours_per_agent = working_hours * (1 - shrinkage_rate) * utilization_target
    tickets_per_agent = (effective_hours_per_agent * 60) / aht_minutes
    max_tickets = math.floor(agents * tickets_per_agent)
    return {
        "effective_hours_per_agent": round(effective_hours_per_agent, 2),
        "tickets_per_agent": round(tickets_per_agent, 1),
        "max_tickets": max_tickets,
    }


def agents_required(ticket_volume, aht_minutes, working_hours, shrinkage_rate, utilization_target):
    effective_hours_per_agent = working_hours * (1 - shrinkage_rate) * utilization_target
    tickets_per_agent = (effective_hours_per_agent * 60) / aht_minutes
    agents_req = math.ceil(ticket_volume / tickets_per_agent)
    return {
        "effective_hours_per_agent": round(effective_hours_per_agent, 2),
        "tickets_per_agent": round(tickets_per_agent, 1),
        "agents_required": agents_req,
    }


def utilization_actual(ticket_volume, aht_minutes, agents, working_hours, shrinkage_rate):
    available_minutes = agents * working_hours * (1 - shrinkage_rate) * 60
    actual_minutes_used = ticket_volume * aht_minutes
    utilization = actual_minutes_used / available_minutes
    return {
        "available_minutes": available_minutes,
        "actual_minutes_used": actual_minutes_used,
        "utilization_rate": round(utilization, 4),
        "utilization_pct": f"{utilization * 100:.2f}%",
    }


def staffing_gap(ticket_volume, aht_minutes, current_agents, working_hours, shrinkage_rate, utilization_target):
    effective_hours_per_agent = working_hours * (1 - shrinkage_rate) * utilization_target
    tickets_per_agent = (effective_hours_per_agent * 60) / aht_minutes
    required = math.ceil(ticket_volume / tickets_per_agent)
    gap = required - current_agents
    if gap > 0:
        recommendation = "hire"
    elif gap < 0:
        recommendation = "surplus"
    else:
        recommendation = "fully staffed"
    return {
        "effective_hours_per_agent": round(effective_hours_per_agent, 2),
        "tickets_per_agent": round(tickets_per_agent, 1),
        "agents_required": required,
        "current_agents": current_agents,
        "gap": gap,
        "recommendation": recommendation,
    }


def regional_summary(roster, projected_tickets, working_hours, shrinkage_rate, utilization_target):
    results = {}
    total_current = 0
    total_required = 0
    total_gap = 0

    for region, data in roster.items():
        result = staffing_gap(
            ticket_volume=projected_tickets[region],
            aht_minutes=data["aht_minutes"],
            current_agents=data["agents"],
            working_hours=working_hours,
            shrinkage_rate=shrinkage_rate,
            utilization_target=utilization_target,
        )
        results[region] = result
        total_current += data["agents"]
        total_required += result["agents_required"]
        total_gap += result["gap"]

    results["GLOBAL"] = {
        "current_agents": total_current,
        "agents_required": total_required,
        "gap": total_gap,
    }
    return results


if __name__ == "__main__":
    th = tickets_handleable(100, 15, 160, 0.20, 0.85)
    print("tickets_handleable:", th)
    assert th["max_tickets"] == 43520, f"Expected 43520, got {th['max_tickets']}"
    print("  max_tickets check PASSED")

    sg = staffing_gap(32500, 12, 50, 160, 0.20, 0.85)
    print("staffing_gap:", sg)
    assert sg["agents_required"] == 60, f"Expected agents_required=60, got {sg['agents_required']}"
    assert sg["gap"] == 10, f"Expected gap=10, got {sg['gap']}"
    print("  agents_required and gap checks PASSED")
