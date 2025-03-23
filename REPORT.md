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
- Interactive map showing all monitoring stations
- Click-to-select station functionality
- Station markers with popup information
- Color-coded markers based on average noise levels

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