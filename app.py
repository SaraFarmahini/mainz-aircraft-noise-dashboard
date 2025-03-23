import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime
import numpy as np

# Set page config
st.set_page_config(
    page_title="Mainz Aircraft Noise Monitoring Dashboard",
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
    'University of Mainz': (49.9900, 8.2700),  # Updated name
    'Mainz/Hechtsheim 2': (49.9700, 8.2900),
    'Mainz/Lerchenberg': (49.9900, 8.2500)
}

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_noise_data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Update station name
    df['station_name'] = df['station_name'].replace('Mainz/Universitätsmedizin', 'University of Mainz')
    return df

def analyze_duplicates(df, station):
    """Analyze duplicate measurements for a station"""
    station_data = df[df['station_name'] == station].copy()
    
    # Find timestamps with multiple measurements
    duplicates = station_data.groupby('datetime').size().reset_index(name='count')
    duplicates = duplicates[duplicates['count'] > 1]
    
    if len(duplicates) > 0:
        # Get detailed information about duplicates
        duplicate_details = station_data[station_data['datetime'].isin(duplicates['datetime'])]
        duplicate_details = duplicate_details.sort_values('datetime')
        
        return {
            'total_duplicates': len(duplicates),
            'max_duplicates': duplicates['count'].max(),
            'duplicate_timestamps': duplicates['datetime'].tolist(),
            'duplicate_details': duplicate_details
        }
    return None

def create_station_map(df):
    # Create a map centered on Mainz using OpenStreetMap
    m = folium.Map(
        location=[49.9925, 8.2473],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add markers for each station
    for station, coords in STATION_COORDS.items():
        station_data = df[df['station_name'] == station]
        avg_noise = station_data['db_a'].mean()
        
        # Create a custom popup with station info
        popup_html = f"""
        <div style="font-family: Arial, sans-serif;">
            <h4>{station}</h4>
            <p>Average Aircraft Noise: {avg_noise:.1f} dB</p>
        </div>
        """
        
        # Add marker with custom icon and popup
        folium.Marker(
            coords,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=station,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    return m

def plot_station_timeseries(df, station, start_date, end_date):
    # Convert date objects to datetime
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)
    
    station_data = df[
        (df['station_name'] == station) & 
        (df['datetime'] >= start_datetime) & 
        (df['datetime'] <= end_datetime)
    ].copy()
    
    if len(station_data) == 0:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for {station} between {start_date} and {end_date}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title=f'Aircraft Noise Levels Over Time - {station}',
            template='plotly_white',
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
    
    fig = px.line(
        station_data,
        x='datetime',
        y='db_a',
        title=f'Aircraft Noise Levels Over Time - {station}',
        labels={'db_a': 'Aircraft Noise Level (dB)', 'datetime': 'Time'}
    )
    
    fig.update_layout(
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def plot_station_heatmap(df, station):
    station_data = df[df['station_name'] == station].copy()
    
    if len(station_data) == 0:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for {station}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title=f'Aircraft Noise Pattern by Hour and Day - {station}',
            template='plotly_white',
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return fig
    
    station_data['hour'] = station_data['datetime'].dt.hour
    station_data['day'] = station_data['datetime'].dt.day
    
    heatmap_data = station_data.pivot_table(
        values='db_a',
        index='hour',
        columns='day',
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        colorbar=dict(title='Aircraft Noise Level (dB)')
    ))
    
    fig.update_layout(
        title=f'Aircraft Noise Pattern by Hour and Day - {station}',
        xaxis_title='Day of Month',
        yaxis_title='Hour of Day',
        template='plotly_white'
    )
    
    return fig

def main():
    st.title("✈️ Mainz Aircraft Noise Monitoring Dashboard")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Get unique stations
    stations = sorted(df['station_name'].unique())
    
    # If no station is selected yet, use the first station as default
    if st.session_state.selected_station is None:
        st.session_state.selected_station = stations[0]
    
    selected_station = st.sidebar.selectbox(
        "Select Station",
        options=stations,
        index=stations.index(st.session_state.selected_station),
        key="station_selector"
    )
    
    # Update session state if station is changed in sidebar
    if selected_station != st.session_state.selected_station:
        st.session_state.selected_station = selected_station
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['datetime'].min().date(), df['datetime'].max().date()),
        min_value=df['datetime'].min().date(),
        max_value=df['datetime'].max().date()
    )
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Station Locations")
        station_map = create_station_map(df)
        # Use st_folium with returned_objects to handle clicks
        map_data = st_folium(
            station_map,
            width=800,
            height=400,
            returned_objects=["last_clicked"]
        )
        
        # Handle map clicks safely
        if map_data and map_data.get('last_clicked'):
            clicked_lat = map_data['last_clicked'].get('lat')
            clicked_lng = map_data['last_clicked'].get('lng')
            
            if clicked_lat is not None and clicked_lng is not None:
                # Find the closest station to the clicked point
                min_dist = float('inf')
                closest_station = None
                
                for station, coords in STATION_COORDS.items():
                    dist = ((coords[0] - clicked_lat) ** 2 + (coords[1] - clicked_lng) ** 2) ** 0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_station = station
                
                if closest_station and min_dist < 0.01:  # Threshold for considering a click "on" a marker
                    st.session_state.selected_station = closest_station
                    st.rerun()
    
    with col2:
        st.subheader("Station Statistics")
        station_data = df[
            (df['station_name'] == st.session_state.selected_station) & 
            (df['datetime'].dt.date >= date_range[0]) & 
            (df['datetime'].dt.date <= date_range[1])
        ]
        
        if len(station_data) == 0:
            st.warning(f"No data available for {st.session_state.selected_station} between {date_range[0]} and {date_range[1]}")
        else:
            # Analyze duplicates
            duplicate_analysis = analyze_duplicates(df, st.session_state.selected_station)
            
            stats = {
                "Average Aircraft Noise": f"{station_data['db_a'].mean():.1f} dB",
                "Maximum Aircraft Noise": f"{station_data['db_a'].max():.1f} dB",
                "Minimum Aircraft Noise": f"{station_data['db_a'].min():.1f} dB",
                "Total Records": f"{len(station_data):,}",
                "Unique Timestamps": f"{len(station_data['datetime'].unique()):,}",
                "Date Range": f"{station_data['datetime'].min().strftime('%Y-%m-%d')} to {station_data['datetime'].max().strftime('%Y-%m-%d')}"
            }
            
            if duplicate_analysis:
                stats["Timestamps with Multiple Measurements"] = f"{duplicate_analysis['total_duplicates']:,}"
                stats["Maximum Measurements per Timestamp"] = f"{duplicate_analysis['max_duplicates']}"
            
            for key, value in stats.items():
                st.metric(key, value)
            
            # Show duplicate analysis if available
            if duplicate_analysis:
                st.subheader("Multiple Measurements Analysis")
                st.write(f"This station has {duplicate_analysis['total_duplicates']} timestamps with multiple measurements.")
                
                # Show a sample of duplicate measurements
                sample_duplicates = duplicate_analysis['duplicate_details'].head(5)
                st.write("Sample of timestamps with multiple measurements:")
                st.dataframe(sample_duplicates[['datetime', 'db_a']].sort_values('datetime'))
    
    # Time series plot
    st.subheader("Time Series Analysis")
    fig_ts = plot_station_timeseries(df, st.session_state.selected_station, date_range[0], date_range[1])
    st.plotly_chart(fig_ts, use_container_width=True)
    
    # Heatmap
    st.subheader("Daily Pattern Analysis")
    fig_hm = plot_station_heatmap(df, st.session_state.selected_station)
    st.plotly_chart(fig_hm, use_container_width=True)
    
    # Monthly averages
    st.subheader("Monthly Average Aircraft Noise Levels")
    monthly_data = df[df['station_name'] == st.session_state.selected_station].copy()
    
    if len(monthly_data) == 0:
        st.warning(f"No data available for {st.session_state.selected_station}")
    else:
        monthly_avg = monthly_data.groupby(
            monthly_data['datetime'].dt.to_period('M')
        )['db_a'].mean().reset_index()
        
        monthly_avg['datetime'] = monthly_avg['datetime'].astype(str)
        fig_monthly = px.line(
            monthly_avg,
            x='datetime',
            y='db_a',
            title=f'Monthly Average Aircraft Noise Levels - {st.session_state.selected_station}',
            labels={'db_a': 'Average Aircraft Noise Level (dB)', 'datetime': 'Month'}
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Add reference to DFLD
    st.markdown("---")
    st.markdown("Reference: Data source: [Deutscher Fluglärmdienst e.V.](https://www.dfld.de/DFLDindex.php?L=G)")

if __name__ == "__main__":
    main() 