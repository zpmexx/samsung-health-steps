import pandas as pd
import glob
import os

def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = glob.glob(os.path.join(script_dir, '*.csv'))
    first_csv = csv_files[0] if csv_files else None
    
    steps_data = pd.read_csv(first_csv, index_col=False)
    
    steps_df = pd.DataFrame(steps_data)
    
    
    filtered_df = steps_df[['update_time','count','source_type']]
    
    filtered_df = steps_df.loc[
    (steps_df['source_type'] == -2),
    ['update_time', 'count']
].sort_values(by='count', ascending=False)




    
    print(filtered_df)
    
    # print("Filtered DataFrame:")
    # print(filtered_df)
    
    
load_data()