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

## Data Access

The processed data file (`cleaned_noise_data.csv`) is stored on DFKI SharePoint. To access the data:

1. Go to [DFKI SharePoint - Sara - Hiwi Climate Health](https://dfkide.sharepoint.com/sites/Team_DSA_Research/Freigegebene%20Dokumente/Forms/AllItems.aspx?csf=1&web=1&e=XWpKoC&ovuser=61a9f1bd%2D7ea0%2D4068%2Db231%2Dbb4a6bfcb700%2Csafa01%40dfki%2Ede&OR=Teams%2DHL&CT=1740240883194&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiI1MC8yNTAxMTYyNDMxOSIsIkhhc0ZlZGVyYXRlZFVzZXIiOmZhbHNlfQ%3D%3D&CID=d60984a1%2Df072%2D0000%2D4ab8%2D55b1f9a4ec8a&cidOR=SPO&FolderCTID=0x012000BF83EA91ED81D34A9516D434481BB75F&id=%2Fsites%2FTeam%5FDSA%5FResearch%2FFreigegebene%20Dokumente%2FPillar%20Spatiotemporal%2FProjects%2FSara%20%2D%20Hiwi%20Climate%20Health&viewid=4423b1fc%2D8f8c%2D46c9%2D9e7c%2D139a85d57b21)
2. Download `cleaned_noise_data.csv`
3. Place it in the same directory as the application files

## Setup

1. Clone this repository
2. Download the data file from DFKI SharePoint (see Data Access section above)
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Select a station from the sidebar or click on the map
2. Choose a date range to analyze
3. View various visualizations and statistics for the selected station 