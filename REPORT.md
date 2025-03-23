# Mainz Aircraft Noise Dashboard Project Report

## Project Overview
This project focuses on creating an interactive dashboard for visualizing aircraft noise data in Mainz, Germany. The dashboard provides spatio-temporal analysis of noise levels across multiple monitoring stations.

## Technical Implementation

### 1. Data Processing
- Cleaned and merged noise monitoring data from multiple stations
- Processed timestamps and standardized data format
- Handled multiple measurements per timestamp
- Created a cleaned dataset (cleaned_noise_data.csv)

### 2. Visualization Features
The dashboard includes several interactive visualizations:

#### Time Series Analysis
- Interactive time series plot showing noise levels over time
- Date range selection for flexible time period analysis
- Station-specific data filtering
- Hover information showing exact noise levels and timestamps

#### Spatial Analysis
The map implementation uses Folium library with the following features:
- Base map centered on Mainz (49.9924° N, 8.2473° E)
- Interactive markers for each monitoring station with precise coordinates:
  - Mainz/Laubenheim 2 (49.9783° N, 8.2792° E)
  - Mainz/Weisenau 2 (49.9850° N, 8.2850° E)
  - Mainz/Oberstadt (49.9950° N, 8.2700° E)
  - Mainz/Ebersheim (49.9200° N, 8.3200° E)
  - Mainz/Hechtsheim 1 (49.9700° N, 8.2900° E)
  - Mainz/Laubenheim (49.9783° N, 8.2792° E)
  - Mainz/Bretzenheim (49.9600° N, 8.2600° E)
  - University of Mainz (49.9900° N, 8.2700° E)
  - Mainz/Hechtsheim 2 (49.9700° N, 8.2900° E)
  - Mainz/Lerchenberg (49.9900° N, 8.2500° E)
- Station marker colors based on average noise levels:
  - Green: < 60 dB
  - Yellow: 60-70 dB
  - Orange: 70-80 dB
  - Red: > 80 dB
- Click-to-select functionality with popup information showing:
  - Station name
  - Average noise level
  - Number of measurements
- Interactive selection that updates all visualizations

#### Heatmap Visualization
- Created using Plotly's density heatmap
- Shows noise level distribution across time periods
- Color scale:
  - Blue: Lower noise levels
  - Green: Medium noise levels
  - Yellow: Higher noise levels
  - Red: Highest noise levels
- Interactive features:
  - Hover information showing exact values
  - Zoom and pan capabilities
  - Time period selection

#### Station Statistics
- Key metrics for each station:
  - Average Aircraft Noise
  - Maximum Aircraft Noise
  - Minimum Aircraft Noise
  - Total Records
  - Date Range

### 3. Technical Stack
- Python 3.10+
- Streamlit for the web interface
- Plotly for interactive visualizations
- Folium for map visualization
- Pandas for data processing
- Git LFS for large file storage

## Implementation Details

### Map Implementation
1. Base Map Setup:
   - Used Folium's Map class with OpenStreetMap tiles
   - Set initial zoom level to 12 for Mainz city view
   - Implemented custom CSS for better marker visibility

2. Station Markers:
   - Created custom marker icons with different colors
   - Added popup information using HTML formatting
   - Implemented click handlers for station selection
   - Added hover effects for better user interaction

3. Interactive Features:
   - Real-time updates of all visualizations on station selection
   - Smooth transitions between selected stations
   - Responsive design that works on both desktop and mobile

### Data Integration
1. Station Data:
   - Stored station coordinates in a Python dictionary
   - Integrated with pandas DataFrame for data filtering
   - Implemented efficient data loading with caching

2. Performance Optimization:
   - Used Streamlit's caching for data loading
   - Implemented efficient data filtering
   - Optimized map rendering for large datasets

## Deployment
The application is deployed on:
1. Streamlit Cloud (public access)
2. GitHub repository: https://github.com/SaraFarmahini/mainz-aircraft-noise-dashboard
3. DFKI GitLab repository: https://git.opendfki.de/sara.farmahini/mainz-aircraft-noise-dashboard

## Data Storage
- Main dataset stored using Git LFS
- Data accessible through both GitHub and DFKI GitLab
- SharePoint integration for additional data storage

## Future Improvements
Potential areas for enhancement:
1. Add more statistical analysis features
2. Implement data export functionality
3. Add more interactive filtering options
4. Enhance mobile responsiveness
5. Add user authentication for sensitive data

## Conclusion
The dashboard successfully provides an interactive platform for analyzing aircraft noise data in Mainz, combining spatial and temporal analysis in a user-friendly interface. The implementation uses modern web technologies and follows best practices for data visualization and deployment. 