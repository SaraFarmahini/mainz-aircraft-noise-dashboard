import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import folium
from folium import plugins

# Read the data
df = pd.read_csv('laubenheim_2012_07.csv')

# Convert datetime column to datetime type
df['datetime'] = pd.to_datetime(df['datetime'])

# Create a time series plot
fig1 = px.line(df, 
               x='datetime', 
               y='db_a',
               title='Noise Levels Over Time at Mainz/Laubenheim',
               labels={'db_a': 'Noise Level (dB)',
                      'datetime': 'Time'})

# Add some styling
fig1.update_layout(
    template='plotly_white',
    hovermode='x unified'
)

# Save the time series plot
fig1.write_html('noise_time_series.html')

# Create a heatmap of noise levels by hour and day
df['hour'] = df['datetime'].dt.hour
df['day'] = df['datetime'].dt.day

# Create pivot table for heatmap
heatmap_data = df.pivot_table(
    values='db_a',
    index='hour',
    columns='day',
    aggfunc='mean'
)

# Create heatmap
fig2 = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale='Viridis',
    colorbar=dict(title='Noise Level (dB)')
))

fig2.update_layout(
    title='Noise Level Heatmap by Hour and Day',
    xaxis_title='Day of Month',
    yaxis_title='Hour of Day',
    template='plotly_white'
)

# Save the heatmap
fig2.write_html('noise_heatmap.html')

# Create a map visualization
# Note: These are approximate coordinates for Mainz/Laubenheim
lat, lon = 49.9783, 8.2792

# Create a map centered on the station
m = folium.Map(location=[lat, lon], zoom_start=13)

# Add a marker for the station
folium.Marker(
    [lat, lon],
    popup='Mainz/Laubenheim Noise Monitoring Station',
    tooltip='Click for details'
).add_to(m)

# Add a heatmap layer
heat_data = [[lat, lon, row['db_a']] for _, row in df.iterrows()]
plugins.HeatMap(heat_data).add_to(m)

# Save the map
m.save('noise_map.html')

print("Visualization files have been created:")
print("1. noise_time_series.html - Interactive time series plot")
print("2. noise_heatmap.html - Interactive heatmap showing patterns by hour and day")
print("3. noise_map.html - Interactive map with station location and heatmap layer") 