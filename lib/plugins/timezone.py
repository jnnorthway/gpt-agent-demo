import pytz
from datetime import datetime


def get_plugin():
    """Get plugin information for OpenAI Assistant."""
    return {
      "type": "function",
      "function": {
        "name": "timezone-get_time",
        "description": "Get the current time for a specific timezone",
        "parameters": {
          "type": "object",
          "properties": {
            "timezone": {
              "type": "string",
              "description": "Time zone, e.g., 'America/New_York', 'Europe/London'"
            },
          },
          "required": ["timezone"]
        }
      }
    }


def get_time(timezone):
    """Get the current time in the given timezone."""
    tz = pytz.timezone(timezone)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z%z")
