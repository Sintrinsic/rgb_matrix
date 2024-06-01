from datetime import datetime
from enum import Enum

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
        pass

    def get_weather(self, date: datetime.date):
        # TODO: Implement the logic to fetch the weather data for the given date
        month = date.month
        day = date.day

        weather_data = {
            'percent_sunny': None, # float from 0 to 100
            'sunny_hours': None, # float from 0 to 24
            'precipitation_hours': None, # float from 0 to 24
            'temp_min': None, #float in F
            'temp_max': None, #float in F
            'weather_code': None, # WeatherCode enum
            'day_length': None # float in hours
        }

        return weather_data