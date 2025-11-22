"""Weather Application using Flet v0.28.3 - Enhanced with Dynamic Colors & Comprehensive Alerts"""

import flet as ft
import asyncio
import httpx
import json
import time
from pathlib import Path
from datetime import datetime
from weather_service import WeatherService, WeatherServiceError
from config import Config


class WeatherApp:
    """Main Weather Application class with enhanced features."""
    
    # Weather condition color schemes
    WEATHER_THEMES = {
        "Clear": {
            "bg": ft.Colors.AMBER_100,
            "primary": ft.Colors.ORANGE_700,
            "secondary": ft.Colors.YELLOW_600,
            "emoji": "☀️",
            "gradient": [ft.Colors.YELLOW_200, ft.Colors.ORANGE_100]
        },
        "Clouds": {
            "bg": ft.Colors.BLUE_GREY_100,
            "primary": ft.Colors.BLUE_GREY_700,
            "secondary": ft.Colors.GREY_600,
            "emoji": "☁️",
            "gradient": [ft.Colors.BLUE_GREY_100, ft.Colors.GREY_200]
        },
        "Rain": {
            "bg": ft.Colors.BLUE_100,
            "primary": ft.Colors.BLUE_700,
            "secondary": ft.Colors.INDIGO_600,
            "emoji": "🌧️",
            "gradient": [ft.Colors.BLUE_200, ft.Colors.BLUE_100]
        },
        "Drizzle": {
            "bg": ft.Colors.LIGHT_BLUE_100,
            "primary": ft.Colors.LIGHT_BLUE_700,
            "secondary": ft.Colors.BLUE_400,
            "emoji": "🌦️",
            "gradient": [ft.Colors.LIGHT_BLUE_200, ft.Colors.LIGHT_BLUE_100]
        },
        "Thunderstorm": {
            "bg": ft.Colors.DEEP_PURPLE_100,
            "primary": ft.Colors.DEEP_PURPLE_700,
            "secondary": ft.Colors.PURPLE_600,
            "emoji": "⛈️",
            "gradient": [ft.Colors.DEEP_PURPLE_200, ft.Colors.INDIGO_100]
        },
        "Snow": {
            "bg": ft.Colors.CYAN_50,
            "primary": ft.Colors.CYAN_700,
            "secondary": ft.Colors.LIGHT_BLUE_400,
            "emoji": "❄️",
            "gradient": [ft.Colors.CYAN_100, ft.Colors.BLUE_50]
        },
        "Mist": {
            "bg": ft.Colors.GREY_100,
            "primary": ft.Colors.GREY_700,
            "secondary": ft.Colors.BLUE_GREY_400,
            "emoji": "🌫️",
            "gradient": [ft.Colors.GREY_200, ft.Colors.BLUE_GREY_50]
        },
        "Fog": {
            "bg": ft.Colors.GREY_100,
            "primary": ft.Colors.GREY_700,
            "secondary": ft.Colors.BLUE_GREY_400,
            "emoji": "🌫️",
            "gradient": [ft.Colors.GREY_200, ft.Colors.BLUE_GREY_50]
        },
        "Haze": {
            "bg": ft.Colors.BROWN_50,
            "primary": ft.Colors.BROWN_400,
            "secondary": ft.Colors.ORANGE_300,
            "emoji": "🌁",
            "gradient": [ft.Colors.BROWN_100, ft.Colors.ORANGE_50]
        }
    }
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        
        # Persistent storage setup
        self.data_dir = Path("weather_app_data")
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "search_history.json"
        self.settings_file = self.data_dir / "settings.json"
        self.watchlist_file = self.data_dir / "watchlist.json"
        
        # Load persistent data
        self.search_history = self.load_history()
        self.settings = self.load_settings()
        self.watchlist = self.load_watchlist()
        
        # Current app state
        self.current_weather_condition = "Clear"
        self.current_city = ""
        self.current_unit = self.settings.get("unit", "metric")
        self.current_weather_data = None
        
        self.setup_page()
        self.build_ui()
        # Initialize UI components
        self.update_history_dropdown()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = 750
        self.page.window.resizable = False
        self.page.window.center()
    
    def load_history(self):
        """Load search history from file. (Feature 1 - Enhanced)"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure we have a list and limit to 10 items
                    return data[:10] if isinstance(data, list) else []
        except Exception as e:
            print(f"Error loading history: {e}")
        return []
    
    def save_history(self):
        """Save search history to file. (Feature 1 - Enhanced)"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_settings(self):
        """Load user settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return {"unit": "metric", "theme": "system"}
    
    def save_settings(self):
        """Save user settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_watchlist(self):
        """Load watchlist cities from file. (Feature 7)"""
        try:
            if self.watchlist_file.exists():
                with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error loading watchlist: {e}")
        return []
    
    def save_watchlist(self):
        """Save watchlist cities to file. (Feature 7)"""
        try:
            with open(self.watchlist_file, 'w', encoding='utf-8') as f:
                json.dump(self.watchlist, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving watchlist: {e}")
    
    def get_weather_theme(self, condition: str):
        """Get theme colors based on weather condition. (Feature 3)"""
        for key in self.WEATHER_THEMES.keys():
            if key.lower() in condition.lower():
                return self.WEATHER_THEMES[key]
        return self.WEATHER_THEMES["Clear"]
    
    def build_ui(self):
        """Build the user interface."""
        # Title with weather emoji
        self.weather_emoji = ft.Text("🌤️", size=40)
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # Theme, location, and unit toggle buttons
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        self.location_button = ft.IconButton(
            icon=ft.Icons.MY_LOCATION,
            tooltip="Use my location",
            on_click=self.on_location_click,
        )
        
        # Unit toggle button (Feature 2)
        self.unit_button = ft.IconButton(
            icon=ft.Icons.THERMOSTAT,
            tooltip=f"Switch to {'Fahrenheit' if self.current_unit == 'metric' else 'Celsius'}",
            on_click=self.toggle_units,
        )
        
        # Title row
        title_row = ft.Row(
            [
                ft.Row([self.weather_emoji, self.title]),
                ft.Row([self.location_button, self.unit_button, self.theme_button]),
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
        
        # City input
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
            width=300,
        )
        
        # Search and forecast buttons
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
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
        
        # Watchlist buttons (Feature 7)
        self.add_to_watchlist_button = ft.ElevatedButton(
            "Add to Watchlist",
            icon=ft.Icons.FAVORITE_BORDER,
            on_click=self.add_to_watchlist,
            visible=False,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.PURPLE_700,
            ),
        )
        
        self.view_watchlist_button = ft.ElevatedButton(
            "View Watchlist",
            icon=ft.Icons.LIST,
            on_click=self.toggle_watchlist_view,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.TEAL_700,
            ),
        )
        
        # Weather alerts container (Feature 6)
        self.alerts_container = ft.Container(
            visible=False,
            padding=15,
            border_radius=10,
            animate=ft.Animation(300, "easeOut"),
        )
        
        # Weather display container (Feature 3 - dynamic colors)
        self.weather_container = ft.Container(
            visible=False,
            border_radius=10,
            padding=20,
            animate_opacity=300,
            animate=ft.Animation(500, "easeInOut"),
        )
        
        # Forecast container (Feature 5)
        self.forecast_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
            animate_opacity=300,
        )
        
        # Watchlist container (Feature 7)
        self.watchlist_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.PURPLE_50,
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
        
        # Main scrollable container
        main_content = ft.Column(
            [
                title_row,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.history_dropdown,
                self.city_input,
                ft.Row([
                    self.search_button,
                    self.forecast_button,
                    self.add_to_watchlist_button,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    self.view_watchlist_button,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.loading,
                self.error_message,
                self.alerts_container,
                self.weather_container,
                self.forecast_container,
                self.watchlist_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Add scroll to the Column
        self.page.add(
            ft.Container(
                content=ft.Column(
                    main_content.controls,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
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
    
    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit. (Feature 2)"""
        if self.current_unit == "metric":
            self.current_unit = "imperial"
            self.unit_button.tooltip = "Switch to Celsius"
        else:
            self.current_unit = "metric"
            self.unit_button.tooltip = "Switch to Fahrenheit"
        
        # Save preference
        self.settings["unit"] = self.current_unit
        self.save_settings()
        
        # Re-fetch weather data with new units if we have a current city
        if self.current_city and self.current_weather_data:
            self.page.run_task(self.get_weather)
        
        self.page.update()
    
    def on_location_click(self, e):
        """Handle location button click."""
        self.page.run_task(self.get_location_weather)
    
    def on_forecast_click(self, e):
        """Handle forecast button click."""
        self.page.run_task(self.get_forecast)
    
    def on_search(self, e):
        """Handle search button click."""
        self.page.run_task(self.get_weather)
    
    def add_to_watchlist(self, e):
        """Add current city to watchlist. (Feature 7)"""
        if self.current_city and self.current_city not in self.watchlist:
            self.watchlist.append(self.current_city)
            self.save_watchlist()
            self.add_to_watchlist_button.text = "Added to Watchlist!"
            self.add_to_watchlist_button.icon = ft.Icons.FAVORITE
            self.page.update()
            
            # Reset button after 2 seconds
            asyncio.create_task(self.reset_watchlist_button())
    
    async def reset_watchlist_button(self):
        """Reset watchlist button after adding."""
        await asyncio.sleep(2)
        self.add_to_watchlist_button.text = "Add to Watchlist"
        self.add_to_watchlist_button.icon = ft.Icons.FAVORITE_BORDER
        self.page.update()
    
    def toggle_watchlist_view(self, e):
        """Toggle watchlist view. (Feature 7)"""
        if self.watchlist_container.visible:
            self.watchlist_container.visible = False
            self.view_watchlist_button.text = "View Watchlist"
        else:
            self.page.run_task(self.display_watchlist)
            self.view_watchlist_button.text = "Hide Watchlist"
        self.page.update()
    
    def add_to_history(self, city: str):
        """Add city to search history with persistent storage. (Feature 1 - Enhanced)"""
        if city and city.strip():
            city = city.strip().title()  # Normalize city name
            if city not in self.search_history:
                self.search_history.insert(0, city)
                self.search_history = self.search_history[:10]  # Keep last 10
                self.save_history()  # Persist to file
                self.update_history_dropdown()
    
    def update_history_dropdown(self):
        """Update the history dropdown display."""
        if self.search_history:
            self.history_dropdown.options = [
                ft.dropdown.Option(c) for c in self.search_history
            ]
            self.history_dropdown.visible = True
        else:
            self.history_dropdown.visible = False
        self.page.update()
    
    def load_from_history(self, e):
        """Load weather from history."""
        if e.control.value:
            self.city_input.value = e.control.value
            self.page.run_task(self.get_weather)
    
    async def get_location_weather(self):
        """Get weather for current location."""
        self.loading.visible = True
        self.error_message.visible = False
        self.page.update()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                lat, lon = data['latitude'], data['longitude']
                city = data.get('city', 'Your Location')
            
            weather_data = await self.weather_service.get_weather_by_coordinates(lat, lon)
            self.city_input.value = city
            self.current_city = city
            self.current_weather_data = weather_data
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
        
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.alerts_container.visible = False
        self.forecast_container.visible = False
        self.forecast_button.visible = False
        self.page.update()
        
        try:
            weather_data = await self.weather_service.get_weather(city, units=self.current_unit)
            self.current_city = city
            self.current_weather_data = weather_data
            self.add_to_history(city)
            await self.display_weather(weather_data)
            self.forecast_button.visible = True
            self.add_to_watchlist_button.visible = True
            
            # Update button state based on watchlist
            if city in self.watchlist:
                self.add_to_watchlist_button.text = "In Watchlist"
                self.add_to_watchlist_button.icon = ft.Icons.FAVORITE
            else:
                self.add_to_watchlist_button.text = "Add to Watchlist"
                self.add_to_watchlist_button.icon = ft.Icons.FAVORITE_BORDER
            
        except WeatherServiceError as e:
            error_msg = str(e)
            if "API key" in error_msg:
                self.show_error(f"🔑 {error_msg}")
            elif "not found" in error_msg:
                self.show_error(f"🏙️ {error_msg}")
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                self.show_error(f"🌐 {error_msg}")
            else:
                self.show_error(f"⚠️ {error_msg}")
        except Exception as e:
            print(f"❌ Unexpected error in get_weather: {str(e)}")  # Debug info
            self.show_error(f"❌ Unexpected error: {str(e)}. Please check the console for details.")
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def get_forecast(self):
        """Fetch and display 5-day forecast. (Feature 5)"""
        city = self.city_input.value.strip()
        
        if not city:
            self.show_error("Please enter a city name first")
            return
        
        self.loading.visible = True
        self.forecast_container.visible = False
        self.page.update()
        
        try:
            forecast_data = await self.weather_service.get_forecast(city, units=self.current_unit)
            await self.display_forecast(forecast_data)
            
        except WeatherServiceError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error("Could not load forecast data")
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    def create_weather_alerts(self, temp: float, feels_like: float, humidity: int, 
                             wind_speed: float, condition: str):
        """Create comprehensive weather alerts. (Feature 6)"""
        alerts = []
        recommendations = []
        
        # Temperature alerts
        if temp > 35:
            alerts.append({
                "icon": ft.Icons.THERMOSTAT,
                "color": ft.Colors.RED_700,
                "title": "🔥 Extreme Heat Alert",
                "message": f"Temperature is {temp:.1f}°C",
                "severity": "high"
            })
            recommendations.append("Stay hydrated and avoid prolonged sun exposure")
            recommendations.append("Wear light, breathable clothing")
        elif temp > 30:
            alerts.append({
                "icon": ft.Icons.WB_SUNNY,
                "color": ft.Colors.ORANGE_700,
                "title": "☀️ High Temperature",
                "message": f"It's quite hot at {temp:.1f}°C",
                "severity": "medium"
            })
            recommendations.append("Drink plenty of water")
            recommendations.append("Apply sunscreen if going outside")
        elif temp < 0:
            alerts.append({
                "icon": ft.Icons.AC_UNIT,
                "color": ft.Colors.CYAN_700,
                "title": "🥶 Freezing Temperature",
                "message": f"Temperature is {temp:.1f}°C",
                "severity": "high"
            })
            recommendations.append("Dress in warm layers")
            recommendations.append("Be careful of icy surfaces")
        elif temp < 10:
            alerts.append({
                "icon": ft.Icons.SEVERE_COLD,
                "color": ft.Colors.LIGHT_BLUE_700,
                "title": "❄️ Cold Weather",
                "message": f"It's cold at {temp:.1f}°C",
                "severity": "medium"
            })
            recommendations.append("Wear a jacket or coat")
        
        # Feels-like temperature difference
        temp_diff = abs(temp - feels_like)
        if temp_diff > 5:
            alerts.append({
                "icon": ft.Icons.THERMOSTAT_AUTO,
                "color": ft.Colors.AMBER_700,
                "title": "🌡️ Temperature Perception Alert",
                "message": f"Feels like {feels_like:.1f}°C (actual: {temp:.1f}°C)",
                "severity": "low"
            })
        
        # Wind alerts
        if wind_speed > 15:
            alerts.append({
                "icon": ft.Icons.AIR,
                "color": ft.Colors.TEAL_700,
                "title": "💨 Strong Wind Alert",
                "message": f"Wind speed: {wind_speed:.1f} m/s",
                "severity": "high"
            })
            recommendations.append("Secure loose objects outdoors")
            recommendations.append("Be cautious when driving")
        elif wind_speed > 10:
            alerts.append({
                "icon": ft.Icons.AIR,
                "color": ft.Colors.BLUE_GREY_700,
                "title": "🌬️ Windy Conditions",
                "message": f"Wind speed: {wind_speed:.1f} m/s",
                "severity": "medium"
            })
            recommendations.append("Hold onto umbrellas tightly")
        
        # Humidity alerts
        if humidity > 80:
            alerts.append({
                "icon": ft.Icons.WATER_DROP,
                "color": ft.Colors.INDIGO_700,
                "title": "💧 High Humidity",
                "message": f"Humidity: {humidity}%",
                "severity": "medium"
            })
            recommendations.append("It may feel muggy and uncomfortable")
        elif humidity < 30:
            alerts.append({
                "icon": ft.Icons.WATER_DROP_OUTLINED,
                "color": ft.Colors.BROWN_400,
                "title": "🏜️ Low Humidity",
                "message": f"Humidity: {humidity}%",
                "severity": "low"
            })
            recommendations.append("Use moisturizer for dry skin")
        
        # Condition-specific alerts
        if "rain" in condition.lower() or "drizzle" in condition.lower():
            recommendations.append("☂️ Bring an umbrella")
            recommendations.append("Drive carefully on wet roads")
        elif "thunder" in condition.lower():
            recommendations.append("⛈️ Stay indoors if possible")
            recommendations.append("Avoid open areas and tall objects")
        elif "snow" in condition.lower():
            recommendations.append("❄️ Watch for slippery roads")
            recommendations.append("Allow extra travel time")
        elif "clear" in condition.lower() and temp > 25:
            recommendations.append("😎 Great weather! Enjoy outdoor activities")
        
        return alerts, recommendations
    
    async def display_weather(self, data: dict):
        """Display weather with dynamic colors and alerts. (Features 3 & 6)"""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        condition = data.get("weather", [{}])[0].get("main", "Clear")
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Get theme for this weather condition (Feature 3)
        theme = self.get_weather_theme(condition)
        self.current_weather_condition = condition
        
        # Update title emoji
        self.weather_emoji.value = theme["emoji"]
        self.page.update()
        
        # Create alerts (Feature 6)
        alerts, recommendations = self.create_weather_alerts(
            temp, feels_like, humidity, wind_speed, description
        )
        
        # Display alerts and/or recommendations if present
        if alerts or recommendations:
            await self.display_alerts(alerts, recommendations, theme)
        
        # Apply gradient background (Feature 3)
        self.weather_container.gradient = ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=theme["gradient"],
        )
        
        # Build weather display with themed colors
        self.weather_container.content = ft.Column(
            [
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=theme["primary"],
                ),
                
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Column([
                            ft.Text(
                                theme["emoji"],
                                size=40,
                            ),
                            ft.Text(
                                description,
                                size=20,
                                italic=True,
                                color=theme["secondary"],
                            ),
                        ]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                ft.Text(
                    f"{temp:.1f}°{'F' if self.current_unit == 'imperial' else 'C'}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=theme["primary"],
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}°{'F' if self.current_unit == 'imperial' else 'C'}",
                    size=16,
                    color=theme["secondary"],
                ),
                
                ft.Text(
                    f"Last updated: {datetime.now().strftime('%H:%M')}",
                    size=12,
                    color=ft.Colors.GREY_600,
                    italic=True,
                ),
                
                ft.Divider(color=theme["secondary"]),
                
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%",
                            theme["primary"]
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed:.1f} m/s",
                            theme["primary"]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Animate appearance
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()
        
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()
    
    async def display_alerts(self, alerts, recommendations, theme):
        """Display weather alerts and recommendations. (Feature 6)
        
        Includes:
        - Extreme weather condition alerts
        - Very high/low temperature warnings
        - Colored banners with icons
        - Personalized recommendations
        """
        alert_cards = []
        
        # Sort by severity: HIGH (red) -> MEDIUM (orange) -> LOW (yellow)
        severity_order = {"high": 0, "medium": 1, "low": 2}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        # Create visually distinct alert cards with severity indicators
        for alert in alerts:
            severity_colors = {
                "high": ft.Colors.RED_100,
                "medium": ft.Colors.ORANGE_100,
                "low": ft.Colors.YELLOW_100
            }
            
            # Severity badge
            severity_badge_color = {
                "high": ft.Colors.RED_700,
                "medium": ft.Colors.ORANGE_700,
                "low": ft.Colors.AMBER_700
            }
            
            severity_text = {
                "high": "⚠️ HIGH",
                "medium": "⚠️ MEDIUM",
                "low": "ℹ️ LOW"
            }
            
            card = ft.Container(
                content=ft.Column(
                    [
                        # Severity badge row
                        ft.Row(
                            [
                                ft.Icon(
                                    alert["icon"],
                                    color=alert["color"],
                                    size=32,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            alert["title"],
                                            weight=ft.FontWeight.BOLD,
                                            size=16,
                                            color=alert["color"],
                                        ),
                                        ft.Text(
                                            alert["message"],
                                            size=13,
                                            color=ft.Colors.BLACK87,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        severity_text.get(alert["severity"], "INFO"),
                                        size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                    bgcolor=severity_badge_color.get(alert["severity"], ft.Colors.GREY_700),
                                    padding=ft.padding.symmetric(8, 4),
                                    border_radius=4,
                                )
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                    ]
                ),
                bgcolor=severity_colors.get(alert["severity"], ft.Colors.GREY_100),
                padding=12,
                border_radius=10,
                border=ft.border.all(3, alert["color"]),
                shadow=ft.BoxShadow(
                    blur_radius=4,
                    spread_radius=0,
                    color=ft.Colors.BLACK12,
                ),
            )
            alert_cards.append(card)
        
        # Always show recommendations card, even if no alerts
        alert_cards_to_show = alert_cards.copy()
        if recommendations:
            rec_items = []
            for rec in recommendations:
                rec_items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("→", size=14, color=ft.Colors.BLUE_700, weight=ft.FontWeight.BOLD),
                            ft.Text(rec, size=12, color=ft.Colors.BLACK87, expand=True),
                        ], spacing=8),
                        padding=ft.padding.symmetric(0, 6),
                    )
                )
            rec_card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LIGHTBULB, color=ft.Colors.BLUE_700, size=24),
                        ft.Text("Recommendations", weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.BLUE_700),
                    ], spacing=8),
                    ft.Divider(height=10, color=ft.Colors.BLUE_200),
                    ft.Column(rec_items, spacing=2),
                ]),
                bgcolor=ft.Colors.LIGHT_BLUE_50,
                padding=15,
                border_radius=10,
                border=ft.border.all(2, ft.Colors.BLUE_300),
                shadow=ft.BoxShadow(blur_radius=3, spread_radius=0, color=ft.Colors.BLACK12),
            )
            alert_cards_to_show.append(rec_card)
        # If no alerts but recommendations exist, show only recommendations
        if not alert_cards and recommendations:
            alert_cards_to_show = [rec_card]
        self.alerts_container.content = ft.Column(alert_cards_to_show, spacing=12)
        
        self.alerts_container.bgcolor = theme["bg"]
        self.alerts_container.visible = True
        self.page.update()
    
    async def display_forecast(self, data: dict):
        """Display 5-day forecast. (Feature 5)"""
        forecast_list = data.get("list", [])
        
        if not forecast_list:
            self.show_error("No forecast data available")
            return
        
        daily_forecasts = []
        seen_dates = set()
        
        # Extract one forecast per day at noon
        for item in forecast_list:
            date = item.get("dt_txt", "").split()[0]
            hour = item.get("dt_txt", "").split()[1] if " " in item.get("dt_txt", "") else ""
            
            if date not in seen_dates and "12:00:00" in hour:
                daily_forecasts.append(item)
                seen_dates.add(date)
                
                if len(daily_forecasts) >= 5:
                    break
        
        forecast_cards = []
        for forecast in daily_forecasts:
            date = forecast.get("dt_txt", "").split()[0]
            temp_max = forecast.get("main", {}).get("temp_max", 0)
            temp_min = forecast.get("main", {}).get("temp_min", 0)
            condition = forecast.get("weather", [{}])[0].get("main", "Clear")
            description = forecast.get("weather", [{}])[0].get("description", "").title()
            icon_code = forecast.get("weather", [{}])[0].get("icon", "01d")
            
            # Get theme for forecast day
            theme = self.get_weather_theme(condition)
            unit_symbol = "°F" if self.current_unit == "imperial" else "°C"
            
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(date, size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(theme["emoji"], size=30),
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}.png",
                            width=50,
                            height=50,
                        ),
                        ft.Text(
                            f"{temp_max:.0f}{unit_symbol} / {temp_min:.0f}{unit_symbol}",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(description, size=10, text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                bgcolor=theme["bg"],
                border_radius=10,
                padding=10,
                width=120,
                border=ft.border.all(2, theme["primary"]),
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
        
        self.forecast_container.opacity = 0
        self.forecast_container.visible = True
        self.page.update()
        
        await asyncio.sleep(0.1)
        self.forecast_container.opacity = 1
        self.page.update()
    
    async def display_watchlist(self):
        """Display multiple cities comparison. (Feature 7)"""
        if not self.watchlist:
            self.watchlist_container.content = ft.Column([
                ft.Text(
                    "No cities in watchlist",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Add cities using the 'Add to Watchlist' button",
                    size=14,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.watchlist_container.visible = True
            self.page.update()
            return
        
        watchlist_cards = []
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text(
                    "🏙️ Cities Watchlist",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PURPLE_700,
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh all",
                    on_click=lambda e: self.page.run_task(self.refresh_watchlist),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
        )
        watchlist_cards.append(header)
        
        # Fetch weather for all watchlist cities
        for city in self.watchlist:
            try:
                weather_data = await self.weather_service.get_weather(city, units=self.current_unit)
                card = self.create_watchlist_city_card(city, weather_data)
                watchlist_cards.append(card)
            except Exception as e:
                # Create error card for failed cities
                error_card = ft.Container(
                    content=ft.Column([
                        ft.Text(f"❌ {city}", weight=ft.FontWeight.BOLD),
                        ft.Text("Failed to load", size=12, color=ft.Colors.RED),
                        ft.ElevatedButton(
                            "Remove",
                            icon=ft.Icons.DELETE,
                            on_click=lambda e, c=city: self.remove_from_watchlist(c),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_100,
                                color=ft.Colors.RED_700,
                            ),
                        ),
                    ]),
                    bgcolor=ft.Colors.RED_50,
                    border_radius=10,
                    padding=15,
                    border=ft.border.all(2, ft.Colors.RED_300),
                )
                watchlist_cards.append(error_card)
        
        self.watchlist_container.content = ft.Column(
            watchlist_cards,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        
        self.watchlist_container.visible = True
        self.page.update()
    
    def create_watchlist_city_card(self, city, weather_data):
        """Create a card for watchlist city display. (Feature 7)"""
        temp = weather_data.get("main", {}).get("temp", 0)
        condition = weather_data.get("weather", [{}])[0].get("main", "Clear")
        description = weather_data.get("weather", [{}])[0].get("description", "").title()
        humidity = weather_data.get("main", {}).get("humidity", 0)
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        
        theme = self.get_weather_theme(condition)
        unit_symbol = "°F" if self.current_unit == "imperial" else "°C"
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(theme["emoji"], size=30),
                        ft.Text(f"{temp:.0f}{unit_symbol}", size=16, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=80,
                ),
                ft.Column([
                    ft.Text(city, size=16, weight=ft.FontWeight.BOLD, color=theme["primary"]),
                    ft.Text(description, size=12, color=theme["secondary"]),
                    ft.Text(f"💧{humidity}% | 💨{wind_speed:.1f}m/s", size=10),
                ], expand=True),
                ft.Column([
                    ft.ElevatedButton(
                        "View",
                        icon=ft.Icons.VISIBILITY,
                        on_click=lambda e, c=city: self.load_city_from_watchlist(c),
                        style=ft.ButtonStyle(
                            bgcolor=theme["primary"],
                            color=ft.Colors.WHITE,
                        ),
                    ),
                    ft.ElevatedButton(
                        "Remove",
                        icon=ft.Icons.DELETE,
                        on_click=lambda e, c=city: self.remove_from_watchlist(c),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.RED_100,
                            color=ft.Colors.RED_700,
                        ),
                    ),
                ]),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=theme["bg"],
            border_radius=10,
            padding=15,
            border=ft.border.all(2, theme["primary"]),
        )
    
    def load_city_from_watchlist(self, city):
        """Load weather for a city from watchlist."""
        self.city_input.value = city
        self.page.run_task(self.get_weather)
    
    def remove_from_watchlist(self, city):
        """Remove city from watchlist."""
        if city in self.watchlist:
            self.watchlist.remove(city)
            self.save_watchlist()
            # Refresh watchlist display if it's currently visible
            if self.watchlist_container.visible:
                self.page.run_task(self.display_watchlist)
    
    async def refresh_watchlist(self):
        """Refresh all watchlist cities."""
        if self.watchlist_container.visible:
            await self.display_watchlist()
    
    def create_info_card(self, icon, label, value, color):
        """Create info card with themed colors."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=color),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=color,
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
        """Display error message with improved formatting."""
        self.error_message.value = message
        self.error_message.visible = True
        self.weather_container.visible = False
        self.alerts_container.visible = False
        self.forecast_container.visible = False
        
        # Print to console for debugging
        print(f"🚫 Error displayed to user: {message}")
        
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)