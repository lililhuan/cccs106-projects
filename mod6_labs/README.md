# Weather Application - Module 6 Lab - Enhanced Edition

## Student Information
- **Name**: [Your Full Name]
- **Student ID**: [Your ID]
- **Course**: CCCS 106
- **Section**: [Your Section]

## Project Overview
A comprehensive weather application built with Python and Flet, featuring dynamic weather-based theming, comprehensive alerts, multiple city management, and persistent data storage. This enhanced version includes 7+ advanced features while maintaining beginner-friendly design.

## Features Implemented

### Base Features
- [x] City search functionality with autocomplete
- [x] Current weather display with dynamic theming
- [x] Temperature, humidity, wind speed with detailed metrics
- [x] Weather icons and emojis
- [x] Comprehensive error handling
- [x] Modern UI with Material Design and animations

### Enhanced Features (7 Features Implemented)

1. **🔍 Search History with Persistent Storage (Enhanced)**
   - Stores last 10 searched cities in JSON file
   - Quick re-search via dropdown selection
   - Prevents duplicates and maintains clean history
   - Data persists across app sessions
   - **Challenge**: Managing file I/O and data validation
   - **Solution**: Implemented robust JSON handling with error recovery

2. **🌡️ Temperature Unit Toggle with Memory**
   - Switch between Celsius and Fahrenheit instantly
   - Remembers user preference across sessions
   - Automatically refetches data with new units
   - Updates all displays in real-time
   - **Challenge**: Maintaining data consistency during unit changes
   - **Solution**: Centralized unit management with automatic refresh

3. **🎨 Weather Condition Icons and Colors (Enhanced)**
   - Dynamic background colors based on weather conditions
   - Gradient effects matching weather types
   - Weather-specific emojis and icons
   - Smooth color transitions and animations
   - **Challenge**: Creating cohesive visual themes
   - **Solution**: Comprehensive theme system with gradient mappings

4. **📅 5-Day Weather Forecast (Enhanced)**
   - Detailed daily forecasts with high/low temperatures
   - Weather icons and descriptions for each day
   - Themed forecast cards matching weather conditions
   - Responsive layout with scroll support
   - **Challenge**: Processing and displaying complex forecast data
   - **Solution**: Smart data parsing with themed presentation

5. **⚠️ Weather Alerts and Warnings (Comprehensive)**
   - Multi-level severity system (HIGH/MEDIUM/LOW)
   - Temperature, wind, and humidity alerts
   - Color-coded banners with descriptive icons
   - Personalized safety recommendations
   - **Challenge**: Creating meaningful alert criteria
   - **Solution**: Research-based thresholds with contextual advice

6. **🏙️ Multiple Cities Watchlist Comparison**
   - Add unlimited cities to personal watchlist
   - Side-by-side weather comparison view
   - Quick actions: view details, refresh, remove
   - Persistent storage with error handling
   - **Challenge**: Managing multiple API calls efficiently
   - **Solution**: Asynchronous processing with graceful error handling

7. **📍 Current Location Weather Detection**
   - IP-based geolocation for automatic city detection
   - One-click location weather fetching
   - Seamless integration with search workflow
   - **Challenge**: Handling location permissions and privacy
   - **Solution**: IP-based detection with clear user feedback

### Bonus Features
- **💾 Persistent Settings**: Theme and unit preferences saved
- **🔄 Auto-Refresh**: Real-time updates with timestamps  
- **📱 Responsive Design**: Mobile-friendly scrollable interface
- **🌓 Dark/Light Theme**: System theme support with manual toggle

## Screenshots
### Main Weather Display with Dynamic Theming
- Current weather with weather-appropriate background colors
- Temperature displayed in user's preferred units
- Real-time weather alerts and recommendations

### 5-Day Forecast View
- Themed forecast cards for next 5 days
- High/low temperatures with weather icons
- Detailed weather descriptions

### Multiple Cities Watchlist
- Side-by-side comparison of multiple cities
- Quick actions for viewing or removing cities
- Real-time weather data for all watchlist cities

### Search History and Settings
- Persistent search history dropdown
- Unit toggle functionality
- Dark/light theme support

## Technical Implementation

### Architecture
```
Weather App/
├── main.py                 # Main application with UI components
├── weather_service.py      # API service layer
├── config.py              # Configuration management  
└── weather_app_data/      # Persistent data storage
    ├── search_history.json
    ├── settings.json
    └── watchlist.json
```

### Key Technologies
- **Flet**: Modern Python GUI framework
- **asyncio**: Asynchronous HTTP requests
- **httpx**: HTTP client for API calls
- **JSON**: Data persistence and API responses
- **OpenWeatherMap API**: Weather data source

### Data Persistence Strategy
The app maintains three persistent data files:
1. **search_history.json**: Last 10 searched cities
2. **settings.json**: User preferences (units, theme)  
3. **watchlist.json**: Saved cities for comparison

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenWeatherMap API key (free registration)

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/<username>/cccs106-projects.git
cd cccs106-projects/mod6_labs

# Create virtual environment
python -m venv cccs106_env
cccs106_env\Scripts\activate  # On Windows
# source cccs106_env/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo OPENWEATHER_API_KEY=your_api_key_here > .env

# Run the application
python main.py
```

### Required Dependencies
```
flet>=0.28.3
httpx>=0.28.0
python-dotenv>=1.0.0
```

## Usage Guide

### Basic Weather Search
1. Enter a city name in the search field
2. Click "Get Weather" or press Enter
3. View current conditions with dynamic theming
4. Check weather alerts and recommendations

### Advanced Features Usage

#### Temperature Units
- Click the thermometer icon to toggle Celsius/Fahrenheit
- Preference is automatically saved for future sessions

#### 5-Day Forecast  
- Search for a city first
- Click "5-Day Forecast" button
- View themed forecast cards for the next 5 days

#### Watchlist Management
1. Search for any city
2. Click "Add to Watchlist" to save the city
3. Click "View Watchlist" to compare multiple cities
4. Use "View" to load a city or "Remove" to delete from watchlist

#### Location Detection
- Click the location pin icon
- App automatically detects your location via IP
- Loads your local weather instantly

## Weather Alerts System

### Alert Categories
- 🔥 **Extreme Heat**: Temperatures > 35°C (95°F)
- 🥶 **Freezing**: Temperatures < 0°C (32°F)  
- ❄️ **Cold Weather**: Temperatures < 10°C (50°F)
- 💨 **Strong Wind**: Wind speed > 15 m/s
- 💧 **High Humidity**: Humidity > 80%
- 🏜️ **Low Humidity**: Humidity < 30%

### Severity Levels
- **🔴 HIGH**: Dangerous conditions requiring immediate attention
- **🟠 MEDIUM**: Notable conditions requiring caution
- **🟡 LOW**: Minor concerns worth noting

## Code Quality Features

### Error Handling
- Comprehensive try-catch blocks for all API calls
- User-friendly error messages
- Graceful degradation for network issues
- Input validation and sanitization

### Performance Optimizations
- Asynchronous API calls for responsive UI
- Efficient data caching in memory
- Lazy loading of forecast data
- Optimized image loading for weather icons

### Maintainability
- Modular code architecture
- Extensive inline documentation
- Clear separation of concerns
- Consistent naming conventions

## Learning Outcomes

This enhanced weather app demonstrates:

✅ **Advanced Python Programming**: Async/await, file I/O, JSON handling  
✅ **Modern GUI Development**: Flet framework, responsive design, animations  
✅ **API Integration**: RESTful services, error handling, data parsing  
✅ **Data Persistence**: Local file storage, settings management  
✅ **User Experience Design**: Intuitive interfaces, visual feedback  
✅ **Software Architecture**: Modular design, separation of concerns  
✅ **Problem Solving**: Feature implementation, debugging, optimization  

## Future Enhancements

Potential improvements for future versions:
- 📊 **Weather Charts**: Historical data visualization
- 🗺️ **Interactive Maps**: Weather overlay mapping
- 🔔 **Push Notifications**: Weather change alerts
- 🎙️ **Voice Input**: Speech recognition for city search
- ⚡ **Offline Mode**: Cached data for offline usage
- 📈 **Weather Trends**: Data analysis and predictions

## Conclusion

This enhanced weather application successfully implements 7+ advanced features while maintaining beginner-friendly design principles. The modular architecture, comprehensive error handling, and extensive documentation make it an excellent demonstration of modern Python GUI development using the Flet framework.
