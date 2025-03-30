import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import numpy as np

# Set page config
st.set_page_config(
    page_title="Mainz Aircraft Noise Dashboard",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state for selected station
if 'selected_station' not in st.session_state:
    st.session_state.selected_station = None

# Station coordinates (approximate)
STATION_COORDS = {
    'Mainz/Laubenheim 2': (49.9783, 8.2792),
    'Mainz/Weisenau 2': (49.9850, 8.2850),
    'Mainz/Oberstadt': (49.9950, 8.2700),
    'Mainz/Ebersheim': (49.9200, 8.3200),
    'Mainz/Hechtsheim 1': (49.9700, 8.2900),
    'Mainz/Laubenheim': (49.9783, 8.2792),
    'Mainz/Bretzenheim': (49.9600, 8.2600),
    'Mainz/Universitätsmedizin': (49.9900, 8.2700),
    'Mainz/Hechtsheim 2': (49.9700, 8.2900),
    'Mainz/Lerchenberg': (49.9900, 8.2500)
}

@st.cache_data
def load_data():
    try:
        # Try reading with different encodings
        encodings = ['utf-8', 'latin1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('cleaned_noise_data.csv', encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            st.error("Could not read the data file with any supported encoding")
            return pd.DataFrame()
        
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Normalize station names to handle encoding issues
        station_mapping = {
            'Mainz/Universit\xef\xbf\xbdtsmedizin': 'Mainz/Universitätsmedizin',
            'Mainz/Universitätsmedizin': 'Mainz/Universitätsmedizin',
            'Mainz/Universit?tsmedizin': 'Mainz/Universitätsmedizin',
            'Mainz/Universitï¿½tsmedizin': 'Mainz/Universitätsmedizin'
        }
        
        df['station_name'] = df['station_name'].replace(station_mapping)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_station_map(df, selected_station, date_range):
    try:
        # Calculate center of Mainz
        center_lat = 49.9929
        center_lon = 8.2473
        
        # Create base map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # Filter data for selected date range
        mask = (df['datetime'] >= date_range[0]) & (df['datetime'] <= date_range[1])
        filtered_df = df[mask]
        
        # Add markers for each station
        for station, coords in STATION_COORDS.items():
            # Calculate average noise level for this station
            station_data = filtered_df[filtered_df['station_name'] == station]
            avg_noise = station_data['db_a'].mean() if not station_data.empty else 0
            
            # Create popup content
            popup_content = f"""
                <div style='font-family: Arial, sans-serif;'>
                    <h4 style='margin: 0;'>{station}</h4>
                    <p style='margin: 5px 0;'>Average Noise: {avg_noise:.1f} dB</p>
                    <p style='margin: 5px 0;'>Total Records: {len(station_data)}</p>
                </div>
            """
            
            # Create marker
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=station,
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None

def create_time_series(df, selected_station, date_range):
    try:
        # Filter data for selected station and date range
        mask = (df['station_name'] == selected_station) & \
               (df['datetime'] >= date_range[0]) & \
               (df['datetime'] <= date_range[1])
        filtered_df = df[mask]
        
        if filtered_df.empty:
            st.warning(f"No data available for {selected_station} in the selected date range")
            return None
        
        # Create time series plot
        fig = px.line(filtered_df, 
                     x='datetime', 
                     y='db_a',
                     title=f'Aircraft Noise Levels at {selected_station}',
                     labels={'db_a': 'Noise Level (dB)', 'datetime': 'Time'},
                     template='plotly_white')
        
        fig.update_layout(
            hovermode='x unified',
            showlegend=False,
            height=400
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating time series plot: {str(e)}")
        return None

def create_heatmap(df, selected_station, date_range):
    try:
        # Filter data for selected station and date range
        mask = (df['station_name'] == selected_station) & \
               (df['datetime'] >= date_range[0]) & \
               (df['datetime'] <= date_range[1])
        filtered_df = df[mask]
        
        if filtered_df.empty:
            st.warning(f"No data available for {selected_station} in the selected date range")
            return None
        
        # Extract hour and day of week
        filtered_df['hour'] = filtered_df['datetime'].dt.hour
        filtered_df['day_of_week'] = filtered_df['datetime'].dt.day_name()
        
        # Create pivot table for heatmap
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_table = filtered_df.pivot_table(
            values='db_a',
            index='day_of_week',
            columns='hour',
            aggfunc='mean'
        ).reindex(day_order)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale='RdYlBu_r',
            colorbar_title='Noise Level (dB)',
            text=np.round(pivot_table.values, 1),
            texttemplate='%{text}',
            textfont={"size": 8}
        ))
        
        fig.update_layout(
            title=f'Daily Noise Pattern at {selected_station}',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=500
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating heatmap: {str(e)}")
        return None

def analyze_duplicates(df, station):
    try:
        # Filter data for selected station
        station_data = df[df['station_name'] == station]
        
        # Find exact duplicates
        exact_duplicates = station_data[station_data.duplicated(subset=['datetime'], keep=False)]
        
        if len(exact_duplicates) > 0:
            st.warning(f"Found {len(exact_duplicates)} exact duplicate records for {station}")
            
            # Show duplicate records
            st.write("Duplicate Records:")
            st.dataframe(exact_duplicates.sort_values('datetime'))
            
            # Calculate statistics for duplicates
            st.write("Statistics for Duplicate Records:")
            st.write(exact_duplicates['db_a'].describe())
        else:
            st.success(f"No exact duplicates found for {station}")
            
        # Find near-duplicates (within 1 second)
        station_data['rounded_time'] = station_data['datetime'].dt.round('1S')
        near_duplicates = station_data[station_data.duplicated(subset=['rounded_time'], keep=False)]
        
        if len(near_duplicates) > 0:
            st.warning(f"Found {len(near_duplicates)} near-duplicate records (within 1 second) for {station}")
            
            # Show near-duplicate records
            st.write("Near-Duplicate Records:")
            st.dataframe(near_duplicates.sort_values('datetime'))
            
            # Calculate statistics for near-duplicates
            st.write("Statistics for Near-Duplicate Records:")
            st.write(near_duplicates['db_a'].describe())
        else:
            st.success(f"No near-duplicates found for {station}")
            
    except Exception as e:
        st.error(f"Error analyzing duplicates: {str(e)}")

def main():
    st.title("✈️ Mainz Aircraft Noise Monitoring Dashboard")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available. Please check the data file.")
        return
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Station selection
    stations = sorted(df['station_name'].unique())
    selected_station = st.sidebar.selectbox(
        "Select Station",
        stations,
        index=stations.index('Mainz/Universitätsmedizin') if 'Mainz/Universitätsmedizin' in stations else 0
    )
    
    # Date range selection
    min_date = df['datetime'].min()
    max_date = df['datetime'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    # Convert date_range to datetime
    date_range = (datetime.combine(date_range[0], datetime.min.time()),
                 datetime.combine(date_range[1], datetime.max.time()))
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Interactive Map")
        m = create_station_map(df, selected_station, date_range)
        if m:
            folium_static(m, width=800, height=500)
    
    with col2:
        st.subheader("Station Statistics")
        # Filter data for selected station and date range
        mask = (df['station_name'] == selected_station) & \
               (df['datetime'] >= date_range[0]) & \
               (df['datetime'] <= date_range[1])
        station_data = df[mask]
        
        if not station_data.empty:
            st.metric("Average Aircraft Noise", f"{station_data['db_a'].mean():.1f} dB")
            st.metric("Maximum Noise Level", f"{station_data['db_a'].max():.1f} dB")
            st.metric("Total Records", f"{len(station_data):,}")
        else:
            st.warning("No data available for the selected station and date range")
    
    # Time series plot
    st.subheader("Time Series Analysis")
    fig_ts = create_time_series(df, selected_station, date_range)
    if fig_ts:
        st.plotly_chart(fig_ts, use_container_width=True)
    
    # Heatmap
    st.subheader("Daily Pattern Heatmap")
    fig_hm = create_heatmap(df, selected_station, date_range)
    if fig_hm:
        st.plotly_chart(fig_hm, use_container_width=True)
    
    # Duplicate analysis
    if st.checkbox("Show Duplicate Analysis"):
        st.subheader("Duplicate Analysis")
        analyze_duplicates(df, selected_station)

if __name__ == "__main__":
    main() 