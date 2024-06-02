from lib.simple_display_client import SimpleDisplayClient
from lib.weather_widgets.weather_fetcher import WeatherFetcher
import pygame
import sys
from datetime import datetime, timedelta
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

# Define the colors based on Solarized Dark mode
BACKGROUND_COLOR = (0, 43, 54)
MAX_TEMP_COLOR = (203, 75, 22)  # Orange-ish
MIN_TEMP_COLOR = (38, 139, 210)  # Teal-ish
SUNSHINE_COLOR = (181, 137, 0)  # Yellow
LIGHT_GRAY = (211, 211, 211)  # Light Gray
DARK_BLUE = (42, 161, 152)  # Dark Blue
GAME_BACKGROUND_COLOR = (0, 0, 0)  # Black

# Path to the custom font file
FONT_PATH = 'fonts/ChakraPetch-Bold.ttf'

def interpolate_color(color1, color2, factor):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

def get_sunshine_color(percentage):
    if percentage >= 90:
        return SUNSHINE_COLOR
    else:
        factor = percentage / 90
        return interpolate_color(LIGHT_GRAY, SUNSHINE_COLOR, factor)

def get_precipitation_color(hours):
    if hours >= 18:
        return DARK_BLUE
    else:
        factor = hours / 18
        return interpolate_color((255, 255, 255), DARK_BLUE, factor)

class WeatherDayWidget:
    def __init__(self, x, y, width, height, weather_data, day_of_week):
        self.rect = pygame.Rect(x, y, width, height)
        self.weather_data = weather_data
        self.day_of_week = day_of_week
        self.font = pygame.font.Font(FONT_PATH, 72)  # Load custom font
        self.day_font = pygame.font.Font(FONT_PATH, 36)  # Smaller font for the day of the week

    def draw(self, surface):
        pygame.draw.rect(surface, BACKGROUND_COLOR, self.rect)

        # Get the colors based on sunshine percentage and precipitation hours
        sunshine_color = get_sunshine_color(round(self.weather_data['percent_sunny']))
        precipitation_color = get_precipitation_color(round(self.weather_data['precipitation_hours']))

        # Render text with rounded values
        day_text = self.font.render(self.day_of_week, True, (255, 255, 255))
        percent_sunny_text = self.font.render(f"{round(self.weather_data['percent_sunny'])}", True, sunshine_color)
        precipitation_hours_text = self.font.render(f"{round(self.weather_data['precipitation_hours'])}", True, precipitation_color)
        temp_max_text = self.font.render(f"{round(self.weather_data['temp_max'])}", True, MAX_TEMP_COLOR)
        temp_min_text = self.font.render(f"{round(self.weather_data['temp_min'])}", True, MIN_TEMP_COLOR)

        # Calculate positions
        text_height = percent_sunny_text.get_height()
        padding = -32
        total_text_height = text_height * 2 + padding * 3
        start_y = self.rect.y -13

        # Blit text
        surface.blit(day_text, (self.rect.centerx - day_text.get_width() // 2, start_y ))
        surface.blit(percent_sunny_text, (self.rect.centerx - percent_sunny_text.get_width() // 2, start_y + text_height + padding))
        surface.blit(precipitation_hours_text, (self.rect.centerx - precipitation_hours_text.get_width() // 2, start_y + (text_height + padding) * 2))
        surface.blit(temp_max_text, (self.rect.centerx - temp_max_text.get_width() // 2, start_y + (text_height + padding) * 3))
        surface.blit(temp_min_text, (self.rect.centerx - temp_min_text.get_width() // 2, start_y + (text_height + padding) * 4))

class WeatherDisplay:
    def __init__(self, x, y, width, height, weather_fetcher):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.weather_fetcher = weather_fetcher
        self.widgets = []
        self.init_widgets()

    def init_widgets(self):
        today = datetime.now().date()
        widget_width = self.width // 5 - 10  # Leave space for borders

        for i in range(5):
            day = today + timedelta(days=i)
            weather_data = self.weather_fetcher.get_weather(day)
            day_of_week = day.strftime('%A')[0]  # Get the first letter of the day of the week
            widget = WeatherDayWidget(self.x + i * (widget_width + 13), self.y, widget_width, self.height, weather_data, day_of_week)
            self.widgets.append(widget)

    def draw(self, surface):
        for widget in self.widgets:
            widget.draw(surface)

class WeatherApp:
    def __init__(self, width, height):
        pygame.init()
        self.client = SimpleDisplayClient(('192.168.1.62', 12345))

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Weather Display")
        self.clock = pygame.time.Clock()
        self.weather_fetcher = WeatherFetcher()
        self.weather_display = WeatherDisplay(0, 0, width, height, self.weather_fetcher)

    def capture_screen(self):
        pygame.display.flip()  # Make sure the latest frame is displayed
        screen_array = pygame.surfarray.array3d(pygame.display.get_surface())
        screen_array = np.transpose(screen_array, (1, 0, 2))  # Transpose to match the correct format
        return screen_array

    def scale_down(self, image_array, size=(64, 32)):
        image = Image.fromarray(image_array)
        image = image.resize(size, Image.LANCZOS)
        image = ImageOps.mirror(image)
        image = image.rotate(90, expand=True)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)  # Increase sharpness
        return np.array(image)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill(GAME_BACKGROUND_COLOR)
            self.weather_display.draw(self.screen)
            pygame.display.flip()
            # Capture the screen data after drawing
            screen_data = self.capture_screen()
            scaled_data = self.scale_down(screen_data)
            print(scaled_data.shape)  # Print the shape to verify the data
            self.client.send_matrix(scaled_data)

            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = WeatherApp(640, 320)
    app.run()
    app.client.close()
