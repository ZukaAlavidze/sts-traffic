import folium
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from config import MAP_CONFIG, DATA_CONFIG

logger = logging.getLogger(__name__)

def create_color_marker(total_vehicles):
    """
    Determine marker color based on total vehicles
    
    Args:
        total_vehicles (int): Total vehicle count
        
    Returns:
        str: Color code for marker
    """
    if total_vehicles < 1000:
        return 'green'
    elif 1000< total_vehicles < 2500:
        return 'orange'
    else:
        return 'red'

def create_map(data, time_interval, selected_date, selected_location=None, project_id=None):
    """
    Create an interactive map with traffic volume markers
    """
    try:
        # Convert selected_date to date object if it's string
        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, DATA_CONFIG['date_format']).date()
        
        # Filter data
        filters = [
            (data['Date'] == selected_date),
            (data['Time Interval'] == time_interval)
        ]
        
        if project_id:
            filters.append(data['Project ID'] == project_id)
            
        filtered_data = data[np.all(filters, axis=0)]
        
        if filtered_data.empty:
            logger.warning("No data available for selected filters")
            return None
        
        # Group by location
        location_summary = filtered_data.groupby(
            ['ID', 'Name', 'LONG', 'LAT', 'Direct_Image_URL']
        )['Total Vehicles'].sum().reset_index()
        
        # Handle invalid coordinates
        mean_lat = location_summary['LAT'].mean()
        mean_long = location_summary['LONG'].mean()
        
        if pd.isna(mean_lat) or pd.isna(mean_long):
            logger.error("Invalid coordinates in data")
            mean_lat = MAP_CONFIG['default_lat']
            mean_long = MAP_CONFIG['default_long']
        
        # Create map
        m = folium.Map(
            location=[mean_lat, mean_long],
            zoom_start=MAP_CONFIG['zoom_start'],
            tiles=MAP_CONFIG['tile_style']
        )

        # Add markers
        for _, row in location_summary.iterrows():
            if pd.isna(row['LAT']) or pd.isna(row['LONG']):
                logger.warning(f"Skipping location {row['ID']} due to invalid coordinates")
                continue
                
            total_vehicles = row['Total Vehicles']
            is_selected = (selected_location == row['ID'])
            
            color = create_color_marker(total_vehicles)
            size = np.log(total_vehicles + 1) * 3
            
            popup_content = f"""
            <div style='width: 220px;'>
                <h4 style="margin:5px 0;">{row['Name']}</h4>
                <b>Total Vehicles:</b> {int(total_vehicles):,}<br>
                <b>Time:</b> {time_interval}
            </div>
            """

            icon_html = f"""
                <div style="
                    width: {size*2}px;
                    height: {size*2}px;
                    background-color: {color};
                    border-radius: 50%;
                    opacity: 0.7;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #fff;
                    font-weight: bold;
                    font-size: {size/2}px;
                    border: 2px solid {'#000' if is_selected else 'transparent'};
                ">
                    {int(total_vehicles):,}
                </div>
            """

            marker = folium.Marker(
                location=[row['LAT'], row['LONG']],
                popup=popup_content,
                icon=folium.DivIcon(html=icon_html),
                options={
                    'clickable': True,
                    'keyboard': False,  # Disable keyboard navigation
                    'riseOnHover': True  # Makes markers more responsive
                }
            ).add_to(m)
        
        return m
        
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        return None

def find_nearest_location(df, lat, lng):
    """
    Find the nearest location ID given latitude and longitude
    """
    if df.empty:
        return None
        
    # Calculate distances to clicked point
    df['distance'] = np.sqrt(
        (df['LAT'] - lat)**2 + 
        (df['LONG'] - lng)**2
    )
    
    # Get ID of closest point
    nearest_loc = df.loc[df['distance'].idxmin(), 'ID']
    df.drop('distance', axis=1, inplace=True)
    
    return nearest_loc