import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
import plotly.subplots as make_subplots

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

@st.cache_data
def load_weather_data():
    try:
        # Read cleaned weather data
        weather_df = pd.read_csv('cleaned_weather_data.csv')
        
        # Convert datetime column
        weather_df['datetime'] = pd.to_datetime(weather_df['datetime'])
        
        return weather_df
    except Exception as e:
        st.error(f"Error loading weather data: {str(e)}")
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

def create_monthly_plot(df, selected_station, date_range):
    try:
        # Filter data for selected station and date range
        mask = (df['station_name'] == selected_station) & \
               (df['datetime'] >= date_range[0]) & \
               (df['datetime'] <= date_range[1])
        filtered_df = df[mask]
        
        if filtered_df.empty:
            st.warning(f"No data available for {selected_station} in the selected date range")
            return None
        
        # Calculate monthly averages
        monthly_avg = filtered_df.groupby(
            filtered_df['datetime'].dt.to_period('M')
        )['db_a'].mean().reset_index()
        
        monthly_avg['datetime'] = monthly_avg['datetime'].astype(str)
        
        # Create monthly plot
        fig = px.line(
            monthly_avg,
            x='datetime',
            y='db_a',
            title=f'Monthly Average Aircraft Noise Levels at {selected_station}',
            labels={'db_a': 'Average Noise Level (dB)', 'datetime': 'Month'},
            template='plotly_white'
        )
        
        fig.update_layout(
            hovermode='x unified',
            showlegend=False,
            height=400,
            xaxis_title='Month',
            yaxis_title='Average Noise Level (dB)'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating monthly plot: {str(e)}")
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

def create_correlation_analysis(df, weather_df, selected_station, date_range):
    try:
        st.subheader("Environmental Factors Analysis")
        
        # Add disclaimer about correlation vs causation
        st.info("""
        ⚠️ **Important Note**: This analysis shows correlations between environmental factors and noise levels. 
        Correlation does not necessarily imply causation. Many factors can influence both variables.
        """)
        
        # Filter data for selected station and date range
        mask = (df['station_name'] == selected_station) & \
               (df['datetime'] >= date_range[0]) & \
               (df['datetime'] <= date_range[1])
        filtered_df = df[mask]
        
        # Filter weather data for selected date range
        weather_mask = (weather_df['datetime'] >= date_range[0]) & (weather_df['datetime'] <= date_range[1])
        filtered_weather = weather_df[weather_mask]
        
        if filtered_df.empty or filtered_weather.empty:
            st.warning("No data available for the selected station and date range")
            return
        
        # Create subplots for environmental factors
        fig = make_subplots(rows=3, cols=1, 
                          subplot_titles=('Aircraft Noise Levels', 'Temperature', 'Humidity'),
                          vertical_spacing=0.1)
        
        # Add noise data
        fig.add_trace(
            go.Scatter(x=filtered_df['datetime'], y=filtered_df['db_a'],
                      name='Noise Level', line=dict(color='red')),
            row=1, col=1
        )
        
        # Add temperature data
        fig.add_trace(
            go.Scatter(x=filtered_weather['datetime'], y=filtered_weather['temperature'],
                      name='Temperature', line=dict(color='orange')),
            row=2, col=1
        )
        
        # Add humidity data
        fig.add_trace(
            go.Scatter(x=filtered_weather['datetime'], y=filtered_weather['humidity'],
                      name='Humidity', line=dict(color='blue')),
            row=3, col=1
        )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"Environmental Factors Analysis for {selected_station}",
            template='plotly_white'
        )
        
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_yaxes(title_text="Noise Level (dB)", row=1, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
        fig.update_yaxes(title_text="Humidity (%)", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate daily averages for correlation analysis
        daily_noise = filtered_df.groupby(filtered_df['datetime'].dt.date)['db_a'].mean().reset_index()
        daily_weather = filtered_weather.groupby(filtered_weather['datetime'].dt.date).agg({
            'temperature': 'mean',
            'humidity': 'mean'
        }).reset_index()
        
        # Merge daily data
        daily_data = pd.merge(daily_noise, daily_weather, 
                            left_on='datetime', 
                            right_on='datetime', 
                            how='inner')
        
        if len(daily_data) < 2:
            st.warning("Not enough data points for correlation analysis")
            return
        
        # Calculate correlations
        st.subheader("Correlation Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Noise vs Temperature
            try:
                temp_corr, temp_p = pearsonr(daily_data['db_a'].values, daily_data['temperature'].values)
                st.metric("Noise vs Temperature Correlation", 
                         f"{temp_corr:.3f}",
                         f"p-value: {temp_p:.3f}")
                
                # Create scatter plot
                fig_temp = px.scatter(daily_data, 
                                    x='db_a', 
                                    y='temperature',
                                    title='Noise vs Temperature',
                                    labels={'db_a': 'Noise Level (dB)', 
                                           'temperature': 'Temperature (°C)'})
                st.plotly_chart(fig_temp, use_container_width=True)
            except Exception as e:
                st.error(f"Error calculating temperature correlation: {str(e)}")
        
        with col2:
            # Noise vs Humidity
            try:
                hum_corr, hum_p = pearsonr(daily_data['db_a'].values, daily_data['humidity'].values)
                st.metric("Noise vs Humidity Correlation", 
                         f"{hum_corr:.3f}",
                         f"p-value: {hum_p:.3f}")
                
                # Create scatter plot
                fig_hum = px.scatter(daily_data, 
                                   x='db_a', 
                                   y='humidity',
                                   title='Noise vs Humidity',
                                   labels={'db_a': 'Noise Level (dB)', 
                                          'humidity': 'Humidity (%)'})
                st.plotly_chart(fig_hum, use_container_width=True)
            except Exception as e:
                st.error(f"Error calculating humidity correlation: {str(e)}")
        
        # Add seasonal analysis
        st.subheader("Seasonal Analysis")
        daily_data['month'] = pd.to_datetime(daily_data['datetime']).dt.month
        monthly_avg = daily_data.groupby('month').agg({
            'db_a': 'mean',
            'temperature': 'mean',
            'humidity': 'mean'
        }).reset_index()
        
        fig_seasonal = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_seasonal.add_trace(
            go.Scatter(x=monthly_avg['month'], y=monthly_avg['db_a'],
                      name='Average Noise', line=dict(color='red')),
            secondary_y=False
        )
        
        fig_seasonal.add_trace(
            go.Scatter(x=monthly_avg['month'], y=monthly_avg['temperature'],
                      name='Average Temperature', line=dict(color='orange')),
            secondary_y=True
        )
        
        fig_seasonal.update_layout(
            title='Monthly Average Noise and Temperature',
            xaxis_title='Month',
            template='plotly_white'
        )
        
        fig_seasonal.update_xaxes(ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                                tickvals=list(range(1, 13)))
        
        fig_seasonal.update_yaxes(title_text="Average Noise Level (dB)", secondary_y=False)
        fig_seasonal.update_yaxes(title_text="Average Temperature (°C)", secondary_y=True)
        
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error in correlation analysis: {str(e)}")
        st.error("Please check if the data contains valid values for correlation analysis.")

def main():
    st.title("✈️ Mainz Aircraft Noise Monitoring Dashboard")
    
    # Load data
    df = load_data()
    weather_df = load_weather_data()
    
    if df.empty:
        st.error("No noise data available. Please check the data file.")
        return
    
    if weather_df.empty:
        st.error("No weather data available. Please check the weather data file.")
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
    
    # Monthly averages plot
    st.subheader("Monthly Average Analysis")
    fig_monthly = create_monthly_plot(df, selected_station, date_range)
    if fig_monthly:
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Heatmap
    st.subheader("Daily Pattern Heatmap")
    fig_hm = create_heatmap(df, selected_station, date_range)
    if fig_hm:
        st.plotly_chart(fig_hm, use_container_width=True)
    
    # Duplicate analysis
    if st.checkbox("Show Duplicate Analysis"):
        st.subheader("Duplicate Analysis")
        analyze_duplicates(df, selected_station)

    # Add correlation analysis section
    st.markdown("---")
    create_correlation_analysis(df, weather_df, selected_station, date_range)

if __name__ == "__main__":
    main() 