import pandas as pd
import glob
import os

def clean_station_name(name):
    """Clean station names by removing 'ooo' and extra spaces"""
    return name.replace('ooo', '').strip()

def process_data():
    # Get all CSV files in the current directory
    csv_files = glob.glob('*.csv')
    
    # List to store all dataframes
    dfs = []
    
    for file in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Clean station names
            df['station_name'] = df['station_name'].apply(clean_station_name)
            
            # Convert datetime column to datetime type
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            # Add year and month columns for easier filtering
            df['year'] = df['datetime'].dt.year
            df['month'] = df['datetime'].dt.month
            
            # Add to list of dataframes
            dfs.append(df)
            
            print(f"Successfully processed {file}")
            
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
    
    # Combine all dataframes
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Sort by datetime
        combined_df = combined_df.sort_values('datetime')
        
        # Remove any duplicates
        combined_df = combined_df.drop_duplicates()
        
        # Save the cleaned and merged data
        combined_df.to_csv('cleaned_noise_data.csv', index=False)
        
        # Print summary statistics
        print("\nData Summary:")
        print(f"Total number of records: {len(combined_df)}")
        print("\nStations:")
        print(combined_df['station_name'].unique())
        print("\nDate range:")
        print(f"From: {combined_df['datetime'].min()}")
        print(f"To: {combined_df['datetime'].max()}")
        print("\nNumber of records per station:")
        print(combined_df['station_name'].value_counts())
        
    else:
        print("No data was processed!")

if __name__ == "__main__":
    process_data() 