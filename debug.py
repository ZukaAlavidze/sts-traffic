import pandas as pd
import logging
from config import DATA_CONFIG
from utils import standardize_column_names

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_data_structure():
    """Analyze and print data structure information for debugging"""
    
    # Check hourly data
    logger.info("Analyzing hourly data structure...")
    try:
        df_hourly = pd.read_csv(DATA_CONFIG['hourly_data'])
        logger.info("Original hourly data columns:")
        logger.info(df_hourly.columns.tolist())
        
        df_hourly = standardize_column_names(df_hourly)
        logger.info("Standardized hourly data columns:")
        logger.info(df_hourly.columns.tolist())
        
        if 'Time Interval' in df_hourly.columns:
            logger.info("Sample Time Intervals (hourly):")
            logger.info(df_hourly['Time Interval'].head())
        else:
            logger.error("Time Interval column not found in hourly data")
            
    except Exception as e:
        logger.error(f"Error processing hourly data: {str(e)}")

    # Check 15-min data
    logger.info("\nAnalyzing 15-minute data structure...")
    try:
        df_15min = pd.read_csv(DATA_CONFIG['fifteen_min_data'])
        logger.info("Original 15-minute data columns:")
        logger.info(df_15min.columns.tolist())
        
        df_15min = standardize_column_names(df_15min)
        logger.info("Standardized 15-minute data columns:")
        logger.info(df_15min.columns.tolist())
        
        if 'Time Interval' in df_15min.columns:
            logger.info("Sample Time Intervals (15-min):")
            logger.info(df_15min['Time Interval'].head())
        else:
            logger.error("Time Interval column not found in 15-minute data")
            
    except Exception as e:
        logger.error(f"Error processing 15-minute data: {str(e)}")

def check_data_consistency():
    """Check data consistency and relationships"""
    try:
        # Load both datasets
        df_hourly = pd.read_csv(DATA_CONFIG['hourly_data'])
        df_15min = pd.read_csv(DATA_CONFIG['fifteen_min_data'])
        
        # Check location IDs
        hourly_locations = set(df_hourly['ID'].unique())
        fifteen_min_locations = set(df_15min['ID'].unique())
        
        logger.info("Location ID Analysis:")
        logger.info(f"Hourly data locations: {hourly_locations}")
        logger.info(f"15-min data locations: {fifteen_min_locations}")
        logger.info(f"Common locations: {hourly_locations & fifteen_min_locations}")
        logger.info(f"Locations only in hourly: {hourly_locations - fifteen_min_locations}")
        logger.info(f"Locations only in 15-min: {fifteen_min_locations - hourly_locations}")
        
        # Check date ranges
        logger.info("\nDate Range Analysis:")
        hourly_dates = pd.to_datetime(df_hourly['Date']).dt.date
        fifteen_min_dates = pd.to_datetime(df_15min['Date']).dt.date
        
        logger.info(f"Hourly data date range: {hourly_dates.min()} to {hourly_dates.max()}")
        logger.info(f"15-min data date range: {fifteen_min_dates.min()} to {fifteen_min_dates.max()}")
        
        # Check for missing values
        logger.info("\nMissing Value Analysis:")
        logger.info("Hourly data missing values:")
        logger.info(df_hourly.isnull().sum())
        logger.info("\n15-min data missing values:")
        logger.info(df_15min.isnull().sum())
        
        # Check data types
        logger.info("\nData Type Analysis:")
        logger.info("Hourly data types:")
        logger.info(df_hourly.dtypes)
        logger.info("\n15-min data types:")
        logger.info(df_15min.dtypes)
        
        # Check for duplicate records
        logger.info("\nDuplicate Record Analysis:")
        hourly_dupes = df_hourly.duplicated().sum()
        fifteen_min_dupes = df_15min.duplicated().sum()
        logger.info(f"Hourly data duplicates: {hourly_dupes}")
        logger.info(f"15-min data duplicates: {fifteen_min_dupes}")
        
    except Exception as e:
        logger.error(f"Error checking data consistency: {str(e)}")

def validate_coordinates():
    """Validate geographic coordinates"""
    try:
        # Load both datasets
        df_hourly = pd.read_csv(DATA_CONFIG['hourly_data'])
        df_15min = pd.read_csv(DATA_CONFIG['fifteen_min_data'])
        
        # Check coordinate ranges
        logger.info("Coordinate Validation:")
        
        # Hourly data
        logger.info("\nHourly Data Coordinates:")
        logger.info(f"LAT range: {df_hourly['LAT'].min()} to {df_hourly['LAT'].max()}")
        logger.info(f"LONG range: {df_hourly['LONG'].min()} to {df_hourly['LONG'].max()}")
        invalid_coords = df_hourly[
            (df_hourly['LAT'].isna()) | 
            (df_hourly['LONG'].isna()) |
            (df_hourly['LAT'] < -90) | 
            (df_hourly['LAT'] > 90) |
            (df_hourly['LONG'] < -180) | 
            (df_hourly['LONG'] > 180)
        ]
        if not invalid_coords.empty:
            logger.error("Invalid coordinates found in hourly data:")
            logger.error(invalid_coords[['ID', 'LAT', 'LONG']])
        
        # 15-min data
        logger.info("\n15-min Data Coordinates:")
        logger.info(f"LAT range: {df_15min['LAT'].min()} to {df_15min['LAT'].max()}")
        logger.info(f"LONG range: {df_15min['LONG'].min()} to {df_15min['LONG'].max()}")
        invalid_coords = df_15min[
            (df_15min['LAT'].isna()) | 
            (df_15min['LONG'].isna()) |
            (df_15min['LAT'] < -90) | 
            (df_15min['LAT'] > 90) |
            (df_15min['LONG'] < -180) | 
            (df_15min['LONG'] > 180)
        ]
        if not invalid_coords.empty:
            logger.error("Invalid coordinates found in 15-min data:")
            logger.error(invalid_coords[['ID', 'LAT', 'LONG']])
            
    except Exception as e:
        logger.error(f"Error validating coordinates: {str(e)}")

if __name__ == "__main__":
    print("Starting data validation and debugging...")
    analyze_data_structure()
    check_data_consistency()
    validate_coordinates()
    print("Data validation and debugging complete.")