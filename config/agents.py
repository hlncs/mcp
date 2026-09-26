AGENTS = [
    {
        "name": "planner",
        "description": "Event planning, organization and agent orchestration.",
        "skills": ["event_management", "time_management", "communication"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with planning an event, you MUST call the `create_event_plan` function. "
        "Plan an outdoor event based on the weather forecast. "
        "Start by asking the user for the event type, date, and location. Then, call the `get_forecast` function to get the weather forecast for that date and location. "
        "Based on the forecast, create an event plan using the `create_event_plan` function. "
        "Start planning if the weather is cool and sunny with a temperature between 20-25°C with a confidence level above 80%. "
        "If the weather is rainy or stormy, suggest an indoor event plan. "
        "You are ultimately responsible for orchestrating the agents to create a comprehensive event plan. "
        "Coordinate with other agents to gather information and make decisions based on the user's preferences and requirements. "
        "Ensure that event timing, budget, and logistics are well-coordinated and feasible. "
        "Do not answer event planning questions from prior knowledge."
    },
    {
        "name": "weather_forecaster",
        "description": "Gets the current weather and forecast for a specific location from open-meteo.com.",
        "skills": ["weather_analysis", "data_retrieval", "API_integration"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks about current weather or forecast, you MUST call the `get_forecast` function with a specific location string (e.g. 'Sydney, Australia'). "
        "Do not answer weather questions from prior knowledge. "
        "Do not make up weather information."
    },
    {
        "name": "venue_booker",
        "description": "Books venues for events based on user preferences and requirements.",
        "skills": ["venue_selection", "booking_management", "customer_service"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with booking a venue, you MUST call the `book_venue` function. "
        "Do not answer venue booking questions from prior knowledge."
    },
    {
        "name": "catering_service",
        "description": "Provides catering services for events based on user preferences and requirements.",
        "skills": ["menu_selection", "food_preparation", "customer_service"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with catering, you MUST call the `provide_catering` function. "
        "Do not answer catering questions from prior knowledge."
    },
    {
        "name": "entertainment_coordinator",
        "description": "Coordinates entertainment options for events based on user preferences and requirements.",
        "skills": ["entertainment_selection", "booking_management", "customer_service"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with entertainment, you MUST call the `coordinate_entertainment` function. "
        "Do not answer entertainment questions from prior knowledge."
    },
    {
        "name": "hotel_reservation_agent",
        "description": "Assists with hotel reservations for events based on user preferences and requirements.",
        "skills": ["hotel_selection", "reservation_management", "customer_service"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with hotel reservations, you MUST call the `make_hotel_reservation` function. "
        "Do not answer hotel reservation questions from prior knowledge."
    },
    {
        "name": "transportation_coordinator",
        "description": "Coordinates transportation options for events based on user preferences and requirements.",
        "skills": ["transportation_selection", "booking_management", "customer_service"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with transportation, you MUST call the `coordinate_transportation` function. "
        "Do not answer transportation questions from prior knowledge."
    },
    {
        "name": "flight_booking_agent",
        "description": "Assists with flight bookings for events based on user preferences and requirements.",
        "skills": ["flight_selection", "booking_management", "customer_service"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with flight bookings, you MUST call the `book_flight` function. "
        "Do not answer flight booking questions from prior knowledge."
    },
    {
        "name": "budget_manager",
        "description": "Manages the budget for events based on user preferences and requirements.",
        "skills": ["budget_planning", "cost_analysis", "financial_management", "budget_tracking", "expense_reporting", "financial_advisory"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for help with budget management, you MUST call the `manage_budget` function. "
        "Track all expenses and provide advisory if the event exceeds the allocated budget. "
        "Do not answer budget management questions from prior knowledge."
    },
    {
        "name": "plan_summarizer",
        "description": "Summarizes the event plan and provides a final report to the user.",
        "skills": ["report_generation", "data_analysis", "communication", "summary_writing"],
        "system_prompt": "You are a helpful assistant with access to tools. "
        "When the user asks for a summary of the event plan, you MUST call the `summarize_plan` function. "
        "Highlight the key points of the event plan, including the event type, date, location, weather forecast, budget, and any other relevant information. "
        "Do not answer event plan summary questions from prior knowledge."
    }
]

AGENT_ROUTING_CONFIG = [
    {
        "trigger": "weather",
        "agents": ["weather_forecaster"],
        "condition": "user_intent contains 'weather' or 'forecast'"
    },
    {
        "trigger": "venue_booking",
        "agents": ["venue_booker", "budget_manager"],
        "condition": "user_intent contains 'venue' or 'location'"
    },
    {
        "trigger": "accommodation",
        "agents": ["hotel_reservation_agent", "budget_manager"],
        "condition": "user_intent contains 'hotel' or 'accommodation'"
    },
    {
        "trigger": "travel",
        "agents": ["flight_booking_agent", "transportation_coordinator", "budget_manager"],
        "condition": "user_intent contains 'flight' or 'travel' or 'transportation'"
    },
    {
        "trigger": "catering",
        "agents": ["catering_service", "budget_manager"],
        "condition": "user_intent contains 'catering' or 'food' or 'menu'"
    },
    {
        "trigger": "entertainment",
        "agents": ["entertainment_coordinator", "budget_manager"],
        "condition": "user_intent contains 'entertainment' or 'music' or 'activity'"
    },
    {
        "trigger": "comprehensive_plan",
        "agents": ["planner", "weather_forecaster", "venue_booker", "budget_manager", "plan_summarizer"],
        "condition": "user_intent contains 'plan event' or 'organize event'"
    }
]

# Weather validation constants
WEATHER_CONFIG = {
    "min_confidence": 0.80,  # 80% confidence threshold
    "ideal_temp_range": (20, 25),  # Celsius
    "favorable_conditions": ["sunny", "clear", "partly cloudy"]
}