TOOLS = [
    {
        "name": "effective_capacity",
        "description": "Calculate total productive hours available for a team given headcount and global assumptions",
        "input_schema": {
            "type": "object",
            "properties": {
                "agents": {"type": "number"},
                "working_hours": {"type": "number"},
                "shrinkage_rate": {"type": "number"},
                "utilization_target": {"type": "number"},
            },
            "required": ["agents", "working_hours", "shrinkage_rate", "utilization_target"],
        },
    },
    {
        "name": "tickets_handleable",
        "description": "Calculate the maximum number of tickets a team can handle given their headcount and handle time",
        "input_schema": {
            "type": "object",
            "properties": {
                "agents": {"type": "number"},
                "aht_minutes": {"type": "number"},
                "working_hours": {"type": "number"},
                "shrinkage_rate": {"type": "number"},
                "utilization_target": {"type": "number"},
            },
            "required": ["agents", "aht_minutes", "working_hours", "shrinkage_rate", "utilization_target"],
        },
    },
    {
        "name": "agents_required",
        "description": "Calculate how many agents are needed to handle a given ticket volume at target utilization",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_volume": {"type": "number"},
                "aht_minutes": {"type": "number"},
                "working_hours": {"type": "number"},
                "shrinkage_rate": {"type": "number"},
                "utilization_target": {"type": "number"},
            },
            "required": ["ticket_volume", "aht_minutes", "working_hours", "shrinkage_rate", "utilization_target"],
        },
    },
    {
        "name": "utilization_actual",
        "description": "Calculate the actual utilization rate a team is running at given their current volume and headcount",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_volume": {"type": "number"},
                "aht_minutes": {"type": "number"},
                "agents": {"type": "number"},
                "working_hours": {"type": "number"},
                "shrinkage_rate": {"type": "number"},
            },
            "required": ["ticket_volume", "aht_minutes", "agents", "working_hours", "shrinkage_rate"],
        },
    },
    {
        "name": "staffing_gap",
        "description": "Calculate net new agents needed to hire (positive) or surplus agents (negative) to meet a ticket volume at target utilization",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_volume": {"type": "number"},
                "aht_minutes": {"type": "number"},
                "current_agents": {"type": "number"},
                "working_hours": {"type": "number"},
                "shrinkage_rate": {"type": "number"},
                "utilization_target": {"type": "number"},
            },
            "required": [
                "ticket_volume",
                "aht_minutes",
                "current_agents",
                "working_hours",
                "shrinkage_rate",
                "utilization_target",
            ],
        },
    },
    {
        "name": "regional_summary",
        "description": "Aggregate staffing gap analysis across all regions returning per-region results and global totals. Call this for any question about global or multi-region headcount.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
