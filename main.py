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

def get_average_steps(dates_steps):
    # Calculate the average steps
    return int(dates_steps['count'].mean().round(0))

def get_median_steps(dates_steps):
    # Calculate the median steps
    return int(dates_steps['count'].median().round(0))

def get_top_steps(dates_steps, top_number):
    # Get the top n days with the most steps
    return dates_steps.nlargest(top_number, 'count')

def get_avg_steps_per_month(dates_steps):
    # Calculate the average steps per month
    dates_steps.index = pd.to_datetime(dates_steps.index)
    dates_steps['month'] = dates_steps.index.to_period('M')
    monthly_avg = dates_steps.groupby('month')['count'].mean().reset_index()
    monthly_avg['month'] = monthly_avg['month'].dt.to_timestamp()

    monthly_avg['month'] = monthly_avg['month'].dt.strftime('%Y-%m')
    monthly_avg['count'] = monthly_avg['count'].round(0).astype(int)
    return monthly_avg

def get_steps_list_to_compare(dates_steps):
    # Get the list of steps to compare
    
    days_count = len(dates_steps)
    steps_list = main_config['steps_list_to_compare']
    steps_list.sort()
    
    steps_count = {step: 0 for step in steps_list}
    
    # Count the number of days for each step target and calculate the percentage
    for step in steps_list:
        steps_count[step] = (len(dates_steps[dates_steps['count'] >= step]),
                             round(len(dates_steps[dates_steps['count'] >= step]) * 100 / days_count,2))

    return steps_count

def get_avg_steps_per_weekday(dates_steps):
    # Get the steps per weekday
    dates_steps.index = pd.to_datetime(dates_steps.index)
    dates_steps['weekday'] = dates_steps.index.day_name()
    weekday_avg = dates_steps.groupby('weekday')['count'].mean().reset_index()
    weekday_avg['count'] = weekday_avg['count'].round(0).astype(int)
    return weekday_avg


# Load data from CSV files
data = load_data()

# Get filtered data for every day from given date range
dates_steps = get_steps_data(data)

#Count the number of days where steps are greater than or equal to the target
target_days_count, total_days_count = count_target_days(dates_steps)

#print(dates_steps)
#print(f"Total days: {total_days_count}")
#print(f"Days with steps >= {main_config['steps_target']}: {target_days_count}")

avg_steps = get_average_steps(dates_steps)
median_steps = get_median_steps(dates_steps)
top_steps = get_top_steps(dates_steps, main_config['top_number'])

avg_steps_per_month = get_avg_steps_per_month(dates_steps)
# Print the results 
print(get_avg_steps_per_weekday(dates_steps))


markdown = f"""[Configuration](#configuration)"""

configuration_markdown = f"""
# Configuration
1. **1. Download from Samsung Health -> settings -> Download personal data**
2. **Extract the zip file and copy the csv file named com.samsung.shealth.step_daily_trend.****.csv into project folder**
3. **Run the main.py script**
"""