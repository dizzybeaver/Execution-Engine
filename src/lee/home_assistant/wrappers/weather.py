"""Weather Wrapper Functions Namespace

5 functions for weather data.

Usage:
    from lee.home_assistant.wrappers import weather

    # Get weather
    weather_data = weather.get_weather(entity_id='weather.home')

    # Get forecast
    forecast = weather.get_forecast(entity_id='weather.home')

    # Get forecasts
    forecasts = weather.get_forecasts(entity_id='weather.home')

    # Get state
    state = weather.get_state(entity_id='weather.home')

    # List weather entities
    entities = weather.list_weather_entities()
"""

# Import all weather wrapper functions
from lee.home_assistant.interface.wrappers.ha_weather_wrappers import (
    get_forecast,
    get_forecasts,
    get_state,
    get_weather,
    list_weather_entities,
)

__all__ = [
    'get_forecast',
    'get_forecasts',
    'get_state',
    'get_weather',
    'list_weather_entities',
]
