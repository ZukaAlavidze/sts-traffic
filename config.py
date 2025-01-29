# Configuration settings for the traffic analysis dashboard
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# App settings
APP_CONFIG = {
    "page_title": "Traffic Volume Analysis Dashboard",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Map settings
MAP_CONFIG = {
    "zoom_start": 14,
    "tile_style": "CartoDB positron",
    "capacity_assumption": 1200,  # vehicles per hour
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

def convert_drive_link(drive_link):
    """Convert Google Drive sharing link to direct image URL"""
    if not isinstance(drive_link, str):
        return None
    
    if not drive_link or 'drive.google.com' not in drive_link:
        return None
    
    try:
        file_id = drive_link.split('/d/')[1].split('/view')[0]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except (IndexError, AttributeError) as e:
        logger.warning(f"Failed to convert drive link: {str(e)}")
        return None

# Column mappings for standardization
COLUMN_MAPPINGS = {
    # Mappings for 15-minute data format
    'location-id': 'ID',
    'location-name': 'Name',
    'time-intervals': 'Time Interval',
    'project-id': 'Project ID',
    'date': 'Date',
    'direction-id': 'Direction ID',
    'total-vehicles': 'Total Vehicles',
    'longitude': 'LONG',
    'latitude': 'LAT',
    'image-url': 'URL',
    'car': 'Car',
    'microbus': 'Microbus',
    'bus': 'Bus',
    'truck': 'Truck',
    'special vehicle': 'Special vehicular',
    'motorcycle': 'Motorcycle',
    'bicycle': 'Bicycle',
    
    # Mappings for hourly data format
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