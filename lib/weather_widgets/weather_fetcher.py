from datetime import datetime, timedelta
from enum import Enum
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pprint import pprint

class WeatherCode(Enum):
    CLEAR_SKY = 0
    MAINLY_CLEAR = 1
    PARTLY_CLOUDY = 2
    OVERCAST = 3
    FOG = 45
    DEPOSITING_RIME_FOG = 48
    LIGHT_DRIZZLE = 51
    MODERATE_DRIZZLE = 53
    DENSE_DRIZZLE = 55
    LIGHT_FREEZING_DRIZZLE = 56
    DENSE_FREEZING_DRIZZLE = 57
    SLIGHT_RAIN = 61
    MODERATE_RAIN = 63
    HEAVY_RAIN = 65
    LIGHT_FREEZING_RAIN = 66
    HEAVY_FREEZING_RAIN = 67
    SLIGHT_SNOWFALL = 71
    MODERATE_SNOWFALL = 73
    HEAVY_SNOWFALL = 75
    SNOW_GRAINS = 77
    SLIGHT_RAIN_SHOWERS = 80
    MODERATE_RAIN_SHOWERS = 81
    VIOLENT_RAIN_SHOWERS = 82
    SLIGHT_SNOW_SHOWERS = 85
    HEAVY_SNOW_SHOWERS = 86
    SLIGHT_THUNDERSTORM = 95
    SLIGHT_THUNDERSTORM_WITH_HAIL = 96
    HEAVY_THUNDERSTORM_WITH_HAIL = 99

class WeatherFetcher:
    '''Class to fetch weather data for a given date. Just create one instance and call get_weather()
     with the date for each day'''

    def __init__(self):
        '''Initialize WeatherFetcher with a cached session and retry logic.'''
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=21600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)

    def get_weather(self, date: datetime.date):
        '''Fetch the weather data for the given date.

        Args:
            date (datetime.date): The date for which to fetch weather data.

        Returns:
            dict: A dictionary containing weather data in the following format:
            'percent_sunny': Float representing the percentage of sunny hours in the day (0-100).
            'sunny_hours': Float representing the number of sunny hours in the day.
            'precipitation_hours': Float representing the number of hours with precipitation in the day.
            'temp_min': Float representing the minimum temperature in Fahrenheit.
            'temp_max': Float representing the maximum temperature in Fahrenheit.
            'weather_code': WeatherCode enum representing the weather code for the day.
            'day_length': Float representing the length of the day in hours.
        '''
        # Define the parameters for the API request
        params = {
            "latitude": 46.758978,
            "longitude": -122.186948,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "daylight_duration", "sunshine_duration", "precipitation_hours"],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "America/Los_Angeles",
            "start_date": date.strftime('%Y-%m-%d'),
            "end_date": (date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        }

        try:
            # Fetch the weather data from the API
            responses = self.openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return {}

        # Process the first location's response
        response = responses[0]
        daily = response.Daily()

        try:
            # Extract the necessary data
            daily_data = {
                "weather_code": daily.Variables(0).ValuesAsNumpy()[0],
                "temperature_2m_max": daily.Variables(1).ValuesAsNumpy()[0],
                "temperature_2m_min": daily.Variables(2).ValuesAsNumpy()[0],
                "daylight_duration": daily.Variables(3).ValuesAsNumpy()[0],
                "sunshine_duration": daily.Variables(4).ValuesAsNumpy()[0],
                "precipitation_hours": daily.Variables(5).ValuesAsNumpy()[0]
            }
        except IndexError as e:
            print(f"Error processing weather data: {e}")
            return {}

        # Calculate the weather data in the desired format
        weather_data = {
            'percent_sunny': (daily_data["sunshine_duration"] / daily_data["daylight_duration"]) * 100 if daily_data["daylight_duration"] else None,
            'sunny_hours': daily_data["sunshine_duration"],
            'precipitation_hours': daily_data["precipitation_hours"],
            'temp_min': daily_data["temperature_2m_min"],
            'temp_max': daily_data["temperature_2m_max"],
            'weather_code': WeatherCode(daily_data["weather_code"]),
            'day_length': daily_data["daylight_duration"] / 3600  # converting seconds to hours
        }

        return weather_data

if __name__ == "__main__":
    # Example use
    # Create an instance of WeatherFetcher
    weather_fetcher = WeatherFetcher()

    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)

    # Fetch the weather data for tomorrow
    weather_data = weather_fetcher.get_weather(tomorrow)

    # Print the weather data
    print("Weather data for tomorrow:")
    for key, value in weather_data.items():
        print(f"{key}: {value}")
