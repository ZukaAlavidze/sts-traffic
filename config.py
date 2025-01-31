from datetime import datetime
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Streamlit page settings
PAGE_CONFIG = {
    "page_title": "STS: Traffic Count Dashboard",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# App settings
APP_CONFIG = {
    "images_path": os.path.join(os.path.dirname(__file__), "static", "images")
}

# Map settings
MAP_CONFIG = {
    "zoom_start": 14,
    "tile_style": "CartoDB positron",
    "default_lat": 0,
    "default_long": 0
}

# Data settings
DATA_CONFIG = {
    "hourly_data": "traffic-count.csv",
    "fifteen_min_data": "traffic-count-15min.csv",
    "date_format": "%Y-%m-%d",
    "chunk_size": 10000
}

# Column mappings for standardization
COLUMN_MAPPINGS = {
    # Mappings for 15-minute data format
    'time-intervals': 'Time Interval',
    'location-id': 'ID',
    'location-name': 'Name',
    'project-id': 'Project ID',
    'date': 'Date',
    'direction-id': 'Direction ID',
    'total-vehicles': 'Total Vehicles',
    'longitude': 'LONG',
    'latitude': 'LAT',
    'car': 'Car',
    'microbus': 'Microbus',
    'bus': 'Bus',
    'truck': 'Truck',
    'special vehicle': 'Special vehicular',
    'motorcycle': 'Motorcycle',
    'bicycle': 'Bicycle',
    
    # Mappings for hourly data format (these stay the same)
    'Project ID': 'Project ID',
    'Date': 'Date',
    'Time Interval': 'Time Interval',
    'Direction ID': 'Direction ID',
    'Car': 'Car',
    'Microbus': 'Microbus',
    'Bus': 'Bus',
    'Truck': 'Truck',
    'Special vehicular': 'Special vehicular',
    'Motorcycle': 'Motorcycle',
    'Bicycle': 'Bicycle',
    'Total Vehicles': 'Total Vehicles',
    'ID': 'ID',
    'Name': 'Name',
    'LONG': 'LONG',
    'LAT': 'LAT',
    'URL': 'URL'
}

# Required columns for data validation
REQUIRED_COLUMNS = {
    'Project ID', 
    'Date', 
    'Time Interval', 
    'Direction ID',
    'Total Vehicles', 
    'ID', 
    'Name', 
    'LONG', 
    'LAT'
}