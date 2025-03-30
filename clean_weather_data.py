import pandas as pd
import numpy as np

def clean_weather_data():
    try:
        # Read weather data
        weather_df = pd.read_csv('dwd/final_merged_data.csv')
        
        # Convert date column to datetime
        weather_df['datetime'] = pd.to_datetime(weather_df['MESS_DATUM'])
        
        # Select relevant columns and rename them
        weather_df = weather_df[['datetime', 'TMK', 'UPM']].rename(columns={
            'TMK': 'temperature',
            'UPM': 'humidity'
        })
        
        # Replace -999 with NaN
        weather_df = weather_df.replace(-999, np.nan)
        
        # Drop rows where both temperature and humidity are NaN
        weather_df = weather_df.dropna(subset=['temperature', 'humidity'], how='all')
        
        # Forward fill missing values (use the last valid value)
        weather_df = weather_df.ffill()
        
        # If there are still missing values at the start, backward fill them
        weather_df = weather_df.bfill()
        
        # Save cleaned data
        weather_df.to_csv('cleaned_weather_data.csv', index=False)
        print("Successfully cleaned and saved weather data to cleaned_weather_data.csv")
        
    except Exception as e:
        print(f"Error cleaning weather data: {str(e)}")

if __name__ == "__main__":
    clean_weather_data() 