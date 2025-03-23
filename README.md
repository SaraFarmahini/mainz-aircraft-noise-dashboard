# Mainz Aircraft Noise Monitoring Dashboard

This interactive dashboard visualizes aircraft noise monitoring data from various stations in Mainz, Germany. The data is sourced from the Deutscher Fluglärmdienst e.V. (DFLD).

## Features

- Interactive map showing all monitoring stations
- Time series analysis of aircraft noise levels
- Daily pattern analysis through heatmaps
- Monthly average noise level trends
- Station-specific statistics
- Date range selection
- Multiple measurement analysis

## Data Source

Data is provided by [Deutscher Fluglärmdienst e.V.](https://www.dfld.de/DFLDindex.php?L=G)

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Select a station from the sidebar or click on the map
2. Choose a date range to analyze
3. View various visualizations and statistics for the selected station 