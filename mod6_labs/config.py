# config.py
"""Configuration management for the Weather App."""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file (explicit path)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

class Config:
    """Application configuration."""
    
    # API Configuration
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    BASE_URL = os.getenv(
        "OPENWEATHER_BASE_URL", 
        "https://api.openweathermap.org/data/2.5/weather"
    )
    
    # App Configuration
    APP_TITLE = "Weather App"
    APP_WIDTH = 400
    APP_HEIGHT = 600
    
    # API Settings
    UNITS = "metric"  # metric, imperial, or standard
    TIMEOUT = 10  # seconds
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.API_KEY:
            # Create .env file with placeholder if it doesn't exist
            env_path = Path(__file__).parent / ".env"
            if not env_path.exists():
                with open(env_path, 'w') as f:
                    f.write("# Weather App Configuration\n")
                    f.write("# Get your free API key from https://openweathermap.org/api\n")
                    f.write("OPENWEATHER_API_KEY=your_api_key_here\n")
                    f.write("\n# Optional: Custom API URL\n")
                    f.write("# OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5/weather\n")
            
            print("\n⚠️  API KEY REQUIRED:")
            print("1. Get a free API key from: https://openweathermap.org/api")
            print(f"2. Edit the .env file at: {env_path}")
            print("3. Replace 'your_api_key_here' with your actual API key")
            print("4. Restart the application\n")
            
            # Don't raise error immediately, let app run with demo mode
            return False
        return True

# Validate configuration on import (but don't fail)
try:
    if Config.validate():
        print("✅ Configuration validated successfully")
except Exception as e:
    print(f"⚠️ Configuration warning: {e}")