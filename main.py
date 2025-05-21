import pandas as pd
import glob
import os
from config import main_config

# load data from CSV files 
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = glob.glob(os.path.join(script_dir, '*.csv'))
    first_csv = csv_files[0] if csv_files else None

    steps_data = pd.read_csv(first_csv, index_col=False, skiprows=1)
    steps_df = pd.DataFrame(steps_data)

    # Convert 'day_time' from milliseconds Unix timestamp to datetime (UTC)
    steps_df['day_time'] = pd.to_datetime(steps_df['day_time'], unit='ms', utc=True)

    # Convdert 'day_time' to date only (we dont need time)
    steps_df['day_time'] = steps_df['day_time'].dt.date

    # Filter your data if needed (e.g., source_type == -2 wchich usualle means sum of both phone and watch)
    steps_df = steps_df[steps_df['source_type'] == -2]
    
    # Sometimes data is duplicated for the same date with different source types, after debugging it shows data from 
    # both phone or watch and sum of both, so we take the max value
    steps_df = steps_df.sort_values('count', ascending=False).drop_duplicates(subset=['day_time'], keep='first')
    
    return steps_df

# Filtered data for every day from given date range
def get_steps_data(steps_df):
    
    filtered_df = steps_df[['day_time', 'count', 'source_type']].copy()
    filtered_df.set_index('day_time', inplace=True)
    
    # Filter data based on the date range in main_config
    start_date = pd.to_datetime(main_config['date_start']).date()
    end_date = pd.to_datetime(main_config['date_end']).date()
    filtered_df = filtered_df[(filtered_df.index >= start_date) & (filtered_df.index <= end_date)]
    
    filtered_df = filtered_df[['count']].sort_values(by='count', ascending=False)

    filtered_df.to_csv('filtered_steps.csv', index=True)
    
    return filtered_df

def count_target_days(dates_steps):
    # Count the number of days where steps are greater than or equal to the target
    target_days = dates_steps[dates_steps['count'] >= main_config['steps_target']]
    return len(target_days), len(dates_steps)


data = load_data()

dates_steps = get_steps_data(data)

#Count the number of days where steps are greater than or equal to the target
target_days_count, total_days_count = count_target_days(dates_steps)

print(dates_steps)
print(f"Total days: {total_days_count}")
print(f"Days with steps >= {main_config['steps_target']}: {target_days_count}")



