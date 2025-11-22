"""Weather API service layer with forecast support and enhanced error handling."""

import httpx
from typing import Dict
from config import Config


class WeatherServiceError(Exception):
    """Custom exception for weather service errors."""
    pass


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.timeout = Config.TIMEOUT
    
    async def get_weather(self, city: str, units: str = None) -> Dict:
        """
        Fetch weather data for a given city.
        
        Args:
            city: Name of the city
            units: Temperature units (metric, imperial, or standard)
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            WeatherServiceError: If the request fails
        """
        if not city:
            raise WeatherServiceError("City name cannot be empty")
        
        # Check if API key is configured
        if not self.api_key or self.api_key == "your_api_key_here" or self.api_key == "":
            raise WeatherServiceError(
                "🔑 API key not configured. Please check your .env file and add a valid OpenWeatherMap API key."
            )
        
        # Build request parameters
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units or Config.UNITS,
        }
        
        print(f"🌐 Making API request for: {city}")  # Debug info
        
        try:
            # Make async HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                
                print(f"📡 API Response Status: {response.status_code}")  # Debug info
                
                # Check for HTTP errors
                if response.status_code == 404:
                    raise WeatherServiceError(
                        f"🏙️ City '{city}' not found. Please check the spelling and try again."
                    )
                elif response.status_code == 401:
                    raise WeatherServiceError(
                        "🔑 Invalid API key. Please check your .env file and verify your OpenWeatherMap API key is correct."
                    )
                elif response.status_code == 429:
                    raise WeatherServiceError(
                        "⏱️ API rate limit exceeded. Please wait a moment and try again."
                    )
                elif response.status_code >= 500:
                    raise WeatherServiceError(
                        "🌐 Weather service is currently unavailable. Please try again later."
                    )
                elif response.status_code != 200:
                    raise WeatherServiceError(
                        f"⚠️ Error fetching weather data (Status: {response.status_code}). Please try again."
                    )
                
                # Parse JSON response
                data = response.json()
                print(f"✅ Successfully fetched weather for {city}")  # Debug info
                return data
                
        except httpx.TimeoutException:
            raise WeatherServiceError(
                "⏱️ Request timed out. Please check your internet connection and try again."
            )
        except httpx.NetworkError as e:
            raise WeatherServiceError(
                f"🌐 Network error: {str(e)}. Please check your internet connection."
            )
        except httpx.HTTPError as e:
            raise WeatherServiceError(f"🌐 HTTP error occurred: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")  # Debug info
            raise WeatherServiceError(f"❌ Unexpected error: {str(e)}. Please try again.")
    
    async def get_weather_by_coordinates(
        self, 
        lat: float, 
        lon: float
    ) -> Dict:
        """
        Fetch weather data by coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary containing weather data
            
        Raises:
            WeatherServiceError: If the request fails
        """
        # Check if API key is configured
        if not self.api_key or self.api_key == "your_api_key_here" or self.api_key == "":
            raise WeatherServiceError(
                "🔑 API key not configured. Please check your .env file and add a valid OpenWeatherMap API key."
            )
        
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": Config.UNITS,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 401:
                    raise WeatherServiceError(
                        "🔑 Invalid API key. Please check your .env file and verify your OpenWeatherMap API key is correct."
                    )
                elif response.status_code != 200:
                    raise WeatherServiceError(
                        f"⚠️ Error fetching weather data: {response.status_code}"
                    )
                
                return response.json()
                
        except httpx.TimeoutException:
            raise WeatherServiceError(
                "⏱️ Request timed out. Please check your internet connection."
            )
        except httpx.NetworkError:
            raise WeatherServiceError(
                "🌐 Network error. Please check your internet connection."
            )
        except Exception as e:
            raise WeatherServiceError(f"❌ Error fetching weather data: {str(e)}")
    
    async def get_forecast(self, city: str, units: str = None) -> Dict:
        """
        Get 5-day weather forecast for a given city.
        
        Args:
            city: Name of the city
            units: Temperature units (metric, imperial, or standard)
            
        Returns:
            Dictionary containing forecast data
            
        Raises:
            WeatherServiceError: If the request fails
        """
        if not city:
            raise WeatherServiceError("City name cannot be empty")
        
        # Check if API key is configured
        if not self.api_key or self.api_key == "your_api_key_here" or self.api_key == "":
            raise WeatherServiceError(
                "🔑 API key not configured. Please check your .env file and add a valid OpenWeatherMap API key."
            )
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units or Config.UNITS,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.forecast_url, params=params)
                
                # Check for HTTP errors
                if response.status_code == 404:
                    raise WeatherServiceError(
                        f"🏙️ City '{city}' not found. Please check the spelling."
                    )
                elif response.status_code == 401:
                    raise WeatherServiceError(
                        "🔑 Invalid API key. Please check your configuration."
                    )
                elif response.status_code >= 500:
                    raise WeatherServiceError(
                        "🌐 Weather service is currently unavailable. Please try again later."
                    )
                elif response.status_code != 200:
                    raise WeatherServiceError(
                        f"⚠️ Error fetching forecast data: {response.status_code}"
                    )
                
                return response.json()
                
        except httpx.TimeoutException:
            raise WeatherServiceError(
                "⏱️ Request timed out. Please check your internet connection."
            )
        except httpx.NetworkError:
            raise WeatherServiceError(
                "🌐 Network error. Please check your internet connection."
            )
        except httpx.HTTPError as e:
            raise WeatherServiceError(f"🌐 HTTP error occurred: {str(e)}")
        except Exception as e:
            raise WeatherServiceError(f"❌ An unexpected error occurred: {str(e)}")