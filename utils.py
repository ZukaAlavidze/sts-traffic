import pandas as pd
import numpy as np
from datetime import datetime
import logging
from config import (
    convert_drive_link, 
    COLUMN_MAPPINGS,
    DATA_CONFIG, 
    REQUIRED_COLUMNS
)

logger = logging.getLogger(__name__)

def standardize_column_names(df):
    """
    Standardize column names across different file formats
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with standardized column names
    """
    # Convert all column names to lowercase and replace hyphens with spaces
    df.columns = df.columns.str.lower().str.replace('-', ' ')
    
    # Create mapping for current columns
    mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        
        # Try to find a matching column in our mapping
        for old_col, new_col in COLUMN_MAPPINGS.items():
            if col_lower == old_col.lower():
                mapping[col] = new_col
                break
    
    # Apply the mapping
    df = df.rename(columns=mapping)
    
    logger.info(f"Standardized columns: {df.columns.tolist()}")
    return df

def validate_dataframe(df):
    """
    Validate DataFrame has required columns and data types
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    # Log current columns for debugging
    logger.info(f"Current columns in DataFrame: {df.columns.tolist()}")
    logger.info(f"Required columns: {REQUIRED_COLUMNS}")
    
    # Check required columns
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        return False, f"Missing required columns: {missing_cols}"
    
    # Check for empty DataFrame
    if df.empty:
        return False, "DataFrame is empty"
    
    # Validate coordinate data
    if df['LAT'].isna().any() or df['LONG'].isna().any():
        logger.warning("Some coordinate data is missing")
    
    return True, ""

def load_data(file_path):
    """
    Load and prepare traffic count data
    
    Args:
        file_path (str): Path to CSV file
        
    Returns:
        pd.DataFrame: Processed DataFrame
        
    Raises:
        ValueError: If data validation fails
        FileNotFoundError: If file doesn't exist
    """
    logger.info(f"Loading data from {file_path}")
    
    try:
        # Read CSV in chunks
        chunks = []
        for chunk in pd.read_csv(file_path, chunksize=DATA_CONFIG['chunk_size']):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
        
        logger.info(f"Original columns: {df.columns.tolist()}")
        
        # Standardize column names
        df = standardize_column_names(df)
        
        logger.info(f"Standardized columns: {df.columns.tolist()}")
        
        # Validate DataFrame
        is_valid, error_msg = validate_dataframe(df)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Convert datetime
        try:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        except Exception as e:
            logger.error(f"Error processing dates: {e}")
            raise ValueError(f"Date conversion failed: {str(e)}")
        
        # Convert image URLs
        if 'URL' in df.columns:
            df['Direct_Image_URL'] = df['URL'].apply(convert_drive_link)
        
        return df
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def calculate_intersection_stats(df, location_id, time_interval, project_id=None):
    """Calculate traffic statistics for a specific intersection"""
    filters = [
        (df['ID'] == location_id),
        (df['Time Interval'] == time_interval)
    ]
    
    if project_id:
        filters.append(df['Project ID'] == project_id)
        
    location_data = df[np.all(filters, axis=0)]
    
    if location_data.empty:
        logger.warning(f"No data found for location {location_id}")
        return {
            'total_vehicles': 0,
            'vehicle_composition': {},
            'percentages': {},
            'image_url': None
        }
    
    # Get vehicle columns
    vehicle_columns = [
        'Car', 'Microbus', 'Bus', 'Truck',
        'Special vehicular', 'Motorcycle', 'Bicycle'
    ]
    
    # Filter to only available vehicle columns
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
    
    image_url = None
    if 'Direct_Image_URL' in location_data.columns and not location_data['Direct_Image_URL'].empty:
        image_url = location_data['Direct_Image_URL'].iloc[0]
    
    return {
        'total_vehicles': total_vehicles,
        'vehicle_composition': vehicle_composition,
        'percentages': percentages,
        'image_url': image_url
    }