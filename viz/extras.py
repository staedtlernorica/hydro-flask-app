def merge_files(file_path):
    import os, xmltodict
    files = os.listdir(file_path)
    merged_readings = []

    for i in files:
        with open(f'{file_path}/{i}') as xml_file:
            data_dict = xmltodict.parse(xml_file.read())

        for i in range(4, len(data_dict['feed']['entry'])):
            metadata = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:interval']
            readings = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:IntervalReading']
            day_start = metadata['espi:start']

            for hourly_readings in readings:       
                reading_start = hourly_readings['espi:timePeriod']['espi:start']
                reading_value = hourly_readings['espi:value']
                merged_readings.append({
                    'day (unix)': day_start,
                    'hour (unix)': reading_start,
                    'reading': reading_value
                })

    return merged_readings

def parse_xml(xml):
    merged_readings = []
    for i in range(4, len(xml['feed']['entry'])):
                metadata = xml['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:interval']
                readings = xml['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:IntervalReading']
                day_start = metadata['espi:start']

                for hourly_readings in readings:       
                    reading_start = hourly_readings['espi:timePeriod']['espi:start']
                    reading_value = hourly_readings['espi:value']
                    merged_readings.append({
                        'day (unix)': day_start,
                        'hour (unix)': reading_start,
                        'reading': reading_value
                    })
    return merged_readings

def assign_season(date):
    import datetime
    fake_date = datetime.datetime(2024, date.month,  date.day).date()
    may_cutoff = datetime.datetime(2024, 4, 30).date()
    nov_cutoff = datetime.datetime(2024, 11, 1).date()
    if may_cutoff < fake_date < nov_cutoff:
        return 'summer'
    else:
        return 'winter'
    
# ASSUMPTION IS THAT THE DATE WHERE THE RATE CHANGES ARE NOT MISSING 
def assign_historical_rates(date_col, plan_rate_change_date_list):
    import numpy as np
    rate_col = date_col.where(date_col.isin(plan_rate_change_date_list), np.nan)
    rate_col = rate_col.ffill()
    rate_dates_in_df = rate_col.dropna().unique()
    dates_not_in_df = [x for x in plan_rate_change_date_list if x not in rate_dates_in_df]
    try:
        prev_rate = max(sorted(dates_not_in_df))
    except:
        prev_rate = np.nan
    rate_col = rate_col.fillna(prev_rate)

    return rate_col

def assign_rate_plan(date, rates_history):
    import numpy as np
    before_dates = [d for d in rates_history if d <= date]
    if before_dates:
        return max(before_dates)
    else:
        return np.nan
    
def get_month_year(readings):
    import pandas as pd
    df = pd.DataFrame(readings)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    df = df.sort_values('hour (unix)')
    df['date (ET)'] = pd.to_datetime(df['hour (unix)'], unit='s', utc=True).dt.tz_convert('America/New_York')
    df['Year-Month'] = df['date (ET)'].dt.strftime('%Y-%m')

    return list(df['Year-Month'].unique())