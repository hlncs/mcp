from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional
from config.agents import AGENT_ROUTING_CONFIG, WEATHER_CONFIG

class EventPlanState(TypedDict):
    user_input: str
    event_type: str
    location: str
    date: str
    weather_data: Optional[Dict[str, Any]]
    bookings: Dict[str, Any]
    budget: float
    budget_remaining: float
    expenses: List[Dict[str, Any]]
    messages: List[str]
    plan_summary: Optional[str]
    current_agent: str

def parse_user_intent(state: EventPlanState) -> EventPlanState:
    """Extract intent and entities from user input"""
    user_input = state["user_input"].lower()

    # Route to appropriate agents based on keywords.
    # Condition format: "user_intent contains 'kw1' or 'kw2'"
    # We extract the quoted keywords and check them against user_input.
    import re
    for routing_rule in AGENT_ROUTING_CONFIG:
        keywords = re.findall(r"'([^']+)'", routing_rule["condition"])
        if any(kw.lower() in user_input for kw in keywords):
            state["current_agent"] = routing_rule["trigger"]
            state["messages"].append(f"Routing to {routing_rule['agents']}")
            break
    
    return state

def validate_weather(state: EventPlanState) -> EventPlanState:
    """Validate if weather conditions are favorable for outdoor events"""
    if not state.get("weather_data"):
        return state
    
    weather = state["weather_data"]
    temp = weather.get("temperature", 0)
    confidence = weather.get("confidence", 0)
    condition = weather.get("condition", "").lower()
    
    is_favorable = (
        WEATHER_CONFIG["ideal_temp_range"][0] <= temp <= WEATHER_CONFIG["ideal_temp_range"][1]
        and confidence >= WEATHER_CONFIG["min_confidence"]
        and any(cond in condition for cond in WEATHER_CONFIG["favorable_conditions"])
    )
    
    if is_favorable:
        state["messages"].append("✅ Weather conditions are favorable for outdoor event!")
    else:
        state["messages"].append("❌ Weather conditions may not be ideal. Consider indoor alternative.")
    
    return state

def track_budget(state: EventPlanState) -> EventPlanState:
    """Track budget and alert if exceeded"""
    total_expenses = sum(exp["amount"] for exp in state["expenses"])
    state["budget_remaining"] = state["budget"] - total_expenses
    
    if state["budget_remaining"] < 0:
        state["messages"].append(f"⚠️ Budget exceeded by ${abs(state['budget_remaining']):.2f}")
    else:
        state["messages"].append(f"💰 Budget remaining: ${state['budget_remaining']:.2f}")
    
    return state

def create_workflow():
    """Create the LangGraph workflow"""
    workflow = StateGraph(EventPlanState)
    
    # Add nodes
    workflow.add_node("parse_intent", parse_user_intent)
    workflow.add_node("validate_weather", validate_weather)
    workflow.add_node("track_budget", track_budget)
    
    # Set entry point
    workflow.set_entry_point("parse_intent")
    
    # Add conditional edges
    workflow.add_edge("parse_intent", "validate_weather")
    workflow.add_edge("validate_weather", "track_budget")
    workflow.add_edge("track_budget", END)
    
    return workflow.compile()

# Instantiate the workflow
event_planning_workflow = create_workflow()