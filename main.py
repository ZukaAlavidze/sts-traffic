import streamlit as st
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from streamlit_folium import folium_static
from config import APP_CONFIG, DATA_CONFIG
from utils import load_data, calculate_intersection_stats
from map_utils import create_map

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Must be the first Streamlit command
st.set_page_config(**APP_CONFIG)

@st.cache_data
def load_css():
    """Load custom CSS styles"""
    try:
        css_path = Path('styles.css')
        if css_path.exists():
            with open(css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        else:
            logger.warning("Custom styling file not found")
    except Exception as e:
        logger.error(f"Error loading CSS: {str(e)}")

@st.cache_data(show_spinner=True)
def load_dataset(data_type):
    """Load and validate dataset based on selected interval"""
    try:
        if data_type == "15 Minutes":
            df = load_data(DATA_CONFIG['fifteen_min_data'])
        else:
            df = load_data(DATA_CONFIG['hourly_data'])
        
        if df is None or df.empty:
            raise ValueError("No data loaded")
            
        # Ensure Date column is properly formatted
        df['Date'] = pd.to_datetime(df['Date']).dt.date
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

def main():
    """Main application function"""
    try:
        # Load CSS
        load_css()
        
        st.title("🚗 Traffic Volume Analysis Dashboard")
        st.write("Interactive dashboard for analyzing intersection traffic data.")

        # ----------------------------------------
        # SIDEBAR CONTROLS
        # ----------------------------------------
        with st.sidebar:
            st.header("⚙️ Analysis Controls")

            # Data type selection
            data_type = st.radio(
                "📊 Select Data Interval",
                options=["1 Hour", "15 Minutes"],
                help="Choose between hourly or 15-minute interval data"
            )
            
            # Load appropriate dataset with loading indicator
            with st.spinner('Loading data...'):
                df = load_dataset(data_type)
            
            if df is None or df.empty:
                st.error("No data available. Please check the data files.")
                return

            # Project selection
            try:
                all_projects = ["All Projects"] + sorted(df['Project ID'].unique().tolist())
                selected_project = st.selectbox(
                    "🏗️ Select Project",
                    options=all_projects,
                    help="Choose a specific project or view all projects"
                )
            except KeyError as e:
                st.error(f"Error: Could not find required column: {str(e)}")
                st.write("Available columns:", df.columns.tolist())
                return

            # Filter data if project is selected
            if selected_project != "All Projects":
                df = df[df['Project ID'] == selected_project]

            # Date filter
            try:
                unique_dates = sorted(df['Date'].unique())
                selected_date = st.selectbox(
                    "📅 Select Date",
                    options=unique_dates,
                    format_func=lambda d: d.strftime(DATA_CONFIG['date_format'])
                )
            except Exception as e:
                st.error(f"Error processing dates: {str(e)}")
                return
            
            # Time interval selection
            try:
                valid_time_intervals = sorted(
                    df[df['Date'] == selected_date]['Time Interval'].unique()
                )
                time_interval = st.selectbox(
                    "🕒 Select Time Interval",
                    options=valid_time_intervals
                )
            except Exception as e:
                st.error(f"Error processing time intervals: {str(e)}")
                return
            
            # Location selection
            try:
                valid_locations = sorted(df['ID'].unique())
                selected_location = st.selectbox(
                    "📍 Select Location",
                    options=valid_locations,
                    format_func=lambda x: f"Location {x}"
                )
            except Exception as e:
                st.error(f"Error processing locations: {str(e)}")
                return

        # ----------------------------------------
        # MAIN CONTENT AREA
        # ----------------------------------------
        
        # First row: Map and Statistics side by side
        col1, col2 = st.columns([2, 1])  # 2:1 ratio for map to stats

        with col1:
            st.subheader("🗺️ Traffic Volume Map")
            with st.spinner('Creating map...'):
                m = create_map(
                    df, 
                    time_interval, 
                    selected_date, 
                    selected_location,
                    selected_project if selected_project != "All Projects" else None
                )
                
                if m is not None:
                    folium_static(m, width=800)
                else:
                    st.warning("Unable to create map with current selection")

        with col2:
            st.subheader("📊 Traffic Statistics")
            with st.spinner('Loading statistics...'):
                stats = calculate_intersection_stats(
                    df, 
                    selected_location, 
                    time_interval,
                    selected_project if selected_project != "All Projects" else None
                )
            
            # Display total vehicles
            st.metric("Total Vehicles", f"{int(stats['total_vehicles']):,}")
            
            # Vehicle composition
            if stats.get('percentages'):
                st.write("##### 🚗 Vehicle Composition")
                for vehicle_type, percentage in stats['percentages'].items():
                    if percentage > 0:
                        st.progress(percentage/100)
                        st.text(f"{vehicle_type}: {percentage:.1f}% ({stats['vehicle_composition'][vehicle_type]:,})")
            else:
                st.info("No vehicle composition data available")

        # Second row: Intersection Image (full width)
        if stats.get('image_url'):
            st.markdown(f"""
                <div class="intersection-image">
                    <h4>📸 Intersection Layout</h4>
                    <img src="{stats['image_url']}" alt="Intersection layout">
                </div>
            """, unsafe_allow_html=True)

        # Third row: Peak Flow Analysis (full width)
        st.subheader("🔄 Peak Flow Analysis")
        direction_data = df[
            (df['ID'] == selected_location) & 
            (df['Time Interval'] == time_interval) &
            (df['Date'] == selected_date)
        ].sort_values('Direction ID')

        if not direction_data.empty:
            st.bar_chart(
                direction_data.set_index('Direction ID')['Total Vehicles'],
                use_container_width=True
            )
        else:
            st.warning("No direction data available for the selected filters")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again or contact support.")
        if st.checkbox("Show error details"):
            st.exception(e)

if __name__ == "__main__":
    main()