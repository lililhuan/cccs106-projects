"""Weather Application using Flet v0.28.3 - Enhanced with Bonus Features"""

import flet as ft
import asyncio
import httpx
from weather_service import WeatherService, WeatherServiceError
from config import Config


class WeatherApp:
    """Main Weather Application class with bonus features."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.search_history = []
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        
        # Add theme switcher - Use system theme
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        
        # Custom theme colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 20
        
        # Window properties
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = 700  # Increased for forecast
        self.page.window.resizable = False
        self.page.window.center()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        # Location button
        self.location_button = ft.IconButton(
            icon=ft.Icons.MY_LOCATION,
            tooltip="Use my location",
            on_click=self.on_location_click,
        )
        
        # Title row with buttons
        title_row = ft.Row(
            [
                self.title,
                ft.Row([
                    self.location_button,
                    self.theme_button,
                ]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Search history dropdown
        self.history_dropdown = ft.Dropdown(
            label="Recent Searches",
            options=[],
            visible=False,
            on_change=self.load_from_history,
            width=300,
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
            width=300,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Forecast toggle button
        self.forecast_button = ft.ElevatedButton(
            "5-Day Forecast",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.on_forecast_click,
            visible=False,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
            ),
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
            animate_opacity=300,
        )
        
        # Forecast container
        self.forecast_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
            animate_opacity=300,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Weather alert banner (initially None)
        self.page.banner = None
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.history_dropdown,
                    self.city_input,
                    ft.Row([
                        self.search_button,
                        self.forecast_button,
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                    self.forecast_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            )
        )
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()
    
    def on_location_click(self, e):
        """Handle location button click."""
        self.page.run_task(self.get_location_weather)
    
    def on_forecast_click(self, e):
        """Handle forecast button click."""
        self.page.run_task(self.get_forecast)
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    def add_to_history(self, city: str):
        """Add city to search history."""
        if city and city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:5]  # Keep last 5
            
            # Update dropdown
            self.history_dropdown.options = [
                ft.dropdown.Option(c) for c in self.search_history
            ]
            self.history_dropdown.visible = len(self.search_history) > 0
            self.page.update()
    
    def load_from_history(self, e):
        """Load weather from history selection."""
        if e.control.value:
            self.city_input.value = e.control.value
            self.page.run_task(self.get_weather)
    
    async def get_location_weather(self):
        """Get weather for current location using IP-based geolocation."""
        self.loading.visible = True
        self.error_message.visible = False
        self.page.update()
        
        try:
            # Get location from IP
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                lat, lon = data['latitude'], data['longitude']
                city = data.get('city', 'Your Location')
            
            # Get weather by coordinates
            weather_data = await self.weather_service.get_weather_by_coordinates(lat, lon)
            
            # Update city input
            self.city_input.value = city
            
            # Display weather
            await self.display_weather(weather_data)
            self.add_to_history(city)
            
        except Exception as e:
            self.show_error("Could not get your location. Please enter city manually.")
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.forecast_button.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Add to history
            self.add_to_history(city)
            
            # Display weather
            await self.display_weather(weather_data)
            
            # Show forecast button
            self.forecast_button.visible = True
            
        except WeatherServiceError as e:
            # Show user-friendly error message
            self.show_error(str(e))
        except Exception as e:
            # Catch any unexpected errors
            self.show_error("An unexpected error occurred. Please try again.")
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def get_forecast(self):
        """Fetch and display 5-day forecast."""
        city = self.city_input.value.strip()
        
        if not city:
            self.show_error("Please enter a city name first")
            return
        
        self.loading.visible = True
        self.forecast_container.visible = False
        self.page.update()
        
        try:
            forecast_data = await self.weather_service.get_forecast(city)
            await self.display_forecast(forecast_data)
            
        except WeatherServiceError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error("Could not load forecast data")
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def display_weather(self, data: dict):
        """Display weather information with animation and alerts."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Check for extreme conditions and show alerts
        self.check_weather_alerts(temp, wind_speed)
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                
                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}°C",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s"
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Fade in animation
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()
        
        # Animate opacity
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()
    
    async def display_forecast(self, data: dict):
        """Display 5-day forecast."""
        forecast_list = data.get("list", [])
        
        if not forecast_list:
            self.show_error("No forecast data available")
            return
        
        # Group forecasts by day (take one per day, around noon)
        daily_forecasts = []
        seen_dates = set()
        
        for item in forecast_list:
            date = item.get("dt_txt", "").split()[0]
            hour = item.get("dt_txt", "").split()[1] if " " in item.get("dt_txt", "") else ""
            
            # Take forecast around noon (12:00:00) for each day
            if date not in seen_dates and "12:00:00" in hour:
                daily_forecasts.append(item)
                seen_dates.add(date)
                
                if len(daily_forecasts) >= 5:
                    break
        
        # Build forecast cards
        forecast_cards = []
        for forecast in daily_forecasts:
            date = forecast.get("dt_txt", "").split()[0]
            temp = forecast.get("main", {}).get("temp", 0)
            description = forecast.get("weather", [{}])[0].get("description", "").title()
            icon_code = forecast.get("weather", [{}])[0].get("icon", "01d")
            
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(date, size=12, weight=ft.FontWeight.BOLD),
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}.png",
                            width=50,
                            height=50,
                        ),
                        ft.Text(f"{temp:.1f}°C", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(description, size=10, text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=10,
                width=120,
            )
            forecast_cards.append(card)
        
        self.forecast_container.content = ft.Column(
            [
                ft.Text("5-Day Forecast", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    forecast_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Fade in animation
        self.forecast_container.opacity = 0
        self.forecast_container.visible = True
        self.page.update()
        
        await asyncio.sleep(0.1)
        self.forecast_container.opacity = 1
        self.page.update()
    
    def check_weather_alerts(self, temp: float, wind_speed: float):
        """Check for extreme weather conditions and show alerts."""
        alerts = []
        
        if temp > 35:
            alerts.append("🔥 High temperature alert! Stay hydrated.")
        elif temp < 0:
            alerts.append("🥶 Freezing temperature! Dress warmly.")
        
        if wind_speed > 10:
            alerts.append("💨 High wind alert! Be cautious outdoors.")
        
        if alerts:
            banner = ft.Banner(
                bgcolor=ft.Colors.AMBER_100,
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
                content=ft.Column([ft.Text(alert) for alert in alerts]),
                actions=[
                    ft.TextButton("OK", on_click=self.close_banner),
                ],
            )
            self.page.banner = banner
            self.page.banner.open = True
            self.page.update()
    
    def close_banner(self, e):
        """Close the alert banner."""
        if self.page.banner:
            self.page.banner.open = False
            self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)