import yaml
import os
from datetime import datetime
from jinja2 import Template
import json

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "data", "templates", "personal_info_template.md")
STATIC_DATA_PATH = os.path.join(BASE_DIR, "data", "static", "personal_info_static.yaml")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "generated", "personal_info.md")

# Ensure directories exist
os.makedirs(os.path.dirname(TEMPLATE_PATH), exist_ok=True)
os.makedirs(os.path.dirname(STATIC_DATA_PATH), exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Mock functions to fetch dynamic data (you would implement these based on your actual data sources)
def fetch_calendar_events():
    """Fetch current calendar events."""
    return """* 9:00 AM - 10:30 AM: Product roadmap meeting with engineering team (Conference Room 3)
* 12:00 PM - 1:00 PM: Lunch with David Wilson
* 2:30 PM - 3:30 PM: Q2 budget review with Victoria
* 5:00 PM - 6:30 PM: Allentown Running Club meetup"""

def fetch_weather():
    """Fetch current weather information."""
    return """Current: 68°F, Partly Cloudy
Today: High 72°F, Low 53°F, 20% chance of rain in the evening
Tomorrow: High 75°F, Low 56°F, Sunny"""

def fetch_tasks():
    """Fetch current task list."""
    return """1. Submit expense report for Chicago trip by EOD
2. Call plumber about leaky faucet in guest bathroom
3. Finish presentation for Thursday's stakeholder meeting
4. Get anniversary gift for Susan
5. Schedule Max's vet appointment"""

def fetch_recent_messages():
    """Fetch summaries of recent important messages."""
    return """* Victoria Martinez (1 hour ago): "Can you send me the updated user metrics before our meeting?"
* Susan (30 minutes ago): "Don't forget we have dinner with the Garcias tonight at 7"
* Emily Chen (15 minutes ago): "The new UI mockups are ready for your review" """

def fetch_health_stats():
    """Fetch current health tracking information."""
    return """* Steps today: 7,234
* Resting heart rate: 65 bpm
* Last night's sleep: 7.1 hours
* Weight: 178 lbs (trending -1.5 lbs this month)"""

def fetch_financial_updates():
    """Fetch recent financial information."""
    return """* Checking balance: $4,285.60
* Credit card balance: $1,240.33 (due in 8 days)
* Recent large transaction: $312.45 at Best Buy (yesterday)
* Monthly budget status: 65% spent, on track"""

def fetch_news_digest():
    """Fetch personalized news digest."""
    return """* Tech: "New Product Management Tools Gaining Traction in Enterprise"
* Local: "Allentown Farmers Market Announces Extended Summer Hours"
* Business: "Market Rebounds After Fed Announcement"
* Sports: "Philadelphia Eagles Sign New Defensive Coordinator" """

def generate_personal_info():
    """Generate the personal info file by combining static and dynamic data."""
    
    # Load the static data
    with open(STATIC_DATA_PATH, 'r') as file:
        static_data = yaml.safe_load(file)
    
    # Load the template
    with open(TEMPLATE_PATH, 'r') as file:
        template_content = file.read()
    
    # Fetch all dynamic data
    dynamic_data = {
        'calendar_events': fetch_calendar_events(),
        'weather_forecast': fetch_weather(),
        'task_list': fetch_tasks(),
        'recent_messages': fetch_recent_messages(),
        'health_stats': fetch_health_stats(),
        'financial_updates': fetch_financial_updates(),
        'news_digest': fetch_news_digest()
    }
    
    # Combine all data for template rendering
    template_data = {**static_data, **dynamic_data}
    
    # Render the template
    template = Template(template_content)
    rendered_content = template.render(**template_data)
    
    # Write the rendered content to the output file
    with open(OUTPUT_PATH, 'w') as file:
        file.write(rendered_content)
    
    print(f"Generated personal info file at: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_personal_info()