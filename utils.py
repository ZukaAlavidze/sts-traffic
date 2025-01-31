import pandas as pd
import os
import numpy as np
from datetime import datetime
import logging
from config import (
    APP_CONFIG,
    COLUMN_MAPPINGS,
    DATA_CONFIG, 
    REQUIRED_COLUMNS
)

logger = logging.getLogger(__name__)

def standardize_column_names(df):
    """
    Standardize column names across different file formats
    """
    df.columns = df.columns.str.lower().str.replace('-', ' ')
    
    mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        for old_col, new_col in COLUMN_MAPPINGS.items():
            if col_lower == old_col.lower():
                mapping[col] = new_col
                break
    
    df = df.rename(columns=mapping)
    logger.info(f"Standardized columns: {df.columns.tolist()}")
    return df

def validate_dataframe(df):
    """
    Validate DataFrame has required columns and data types
    """
    logger.info(f"Current columns in DataFrame: {df.columns.tolist()}")
    logger.info(f"Required columns: {REQUIRED_COLUMNS}")
    
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        return False, f"Missing required columns: {missing_cols}"
    
    if df.empty:
        return False, "DataFrame is empty"
    
    # Fixed: Use correct case for column names
    if df['LAT'].isna().any() or df['LONG'].isna().any():
        logger.warning("Some coordinate data is missing")
    
    return True, ""

def load_data(file_path):
    """
    Load and prepare traffic count data
    """
    logger.info(f"Loading data from {file_path}")
    
    try:
        chunks = []
        for chunk in pd.read_csv(file_path, chunksize=DATA_CONFIG['chunk_size']):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
        
        df = standardize_column_names(df)
        
        is_valid, error_msg = validate_dataframe(df)
        if not is_valid:
            raise ValueError(error_msg)
        
        try:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        except Exception as e:
            logger.error(f"Error processing dates: {e}")
            raise ValueError(f"Date conversion failed: {str(e)}")
        
        # Set image paths for local files - removing any existing 'loc' prefix
        if 'ID' in df.columns:
            df['Direct_Image_URL'] = df['ID'].apply(lambda x: 
                os.path.join(APP_CONFIG['images_path'], 
                           f'loc{str(x).lower().replace("loc", "")}.png'))
            logger.info(f"Added image paths. Sample path: {df['Direct_Image_URL'].iloc[0]}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def calculate_intersection_stats(df, location_id, time_interval, project_id=None):
    """
    Calculate traffic statistics for a specific intersection
    """
    filters = [
        (df['ID'] == location_id),
        (df['Time Interval'] == time_interval)
    ]
    
    if project_id:
        filters.append(df['Project ID'] == project_id)
        
    # Drop duplicates before processing
    location_data = df[np.all(filters, axis=0)].drop_duplicates(subset=['ID', 'Time Interval', 'Direction ID'])
    
    if location_data.empty:
        logger.warning(f"No data found for location {location_id}")
        return {
            'total_vehicles': 0,
            'vehicle_composition': {},
            'percentages': {},
            'image_url': None
        }
    
    vehicle_columns = [
        'Car', 'Microbus', 'Bus', 'Truck',
        'Special vehicular', 'Motorcycle', 'Bicycle'
    ]
    
    # Get single image URL (avoid duplicates)
    image_url = None
    if 'Direct_Image_URL' in location_data.columns:
        unique_urls = location_data['Direct_Image_URL'].unique()
        if len(unique_urls) > 0:
            image_url = unique_urls[0]
            logger.info(f"Selected image URL: {image_url}")
    
    available_columns = [col for col in vehicle_columns if col in location_data.columns]
    total_vehicles = location_data['Total Vehicles'].sum()
    
    vehicle_composition = {
        col: location_data[col].sum()
        for col in available_columns
    }
    
    percentages = {
        vehicle: (count / total_vehicles * 100)
        for vehicle, count in vehicle_composition.items()
        if total_vehicles > 0
    }
    
    return {
        'total_vehicles': total_vehicles,
        'vehicle_composition': vehicle_composition,
        'percentages': percentages,
        'image_url': image_url
    }