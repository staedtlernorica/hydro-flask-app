import os
print(os.curdir)
print(os.listdir())

def parse_xml(xml_file):
    import xmltodict, json
    data_dict = xmltodict.parse(xml_file.read())
    json_data = json.dumps(data_dict)
    parsed = []

    for i in range(4, len(data_dict['feed']['entry'])):
        metadata = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:interval']
        readings = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:IntervalReading']
        day_start = metadata['espi:start']

        for hourly_readings in readings:       
            reading_start = hourly_readings['espi:timePeriod']['espi:start']
            reading_value = hourly_readings['espi:value']
            parsed.append({
                'day (unix)': day_start,
                'hour (unix)': reading_start,
                'reading': reading_value
            })
            
    return parsed

# def merge_readings(*dir):
#     import os
#     files = os.listdir('./static/files/')
#     # files = os.listdir(os.curdir)
#     x = list(filter(lambda x: 'TH_Electric_Usage_' in x, files))
#     # print(args)
#     print('THE FILES ARE ', files)

#     import xmltodict, json
#     merged_readings = []

#     with open(f'{dir}/{file_name}') as xml_file:
#         data_dict = xmltodict.parse(xml_file.read())
#         json_data = json.dumps(data_dict)
        
#         for i in range(4, len(data_dict['feed']['entry'])):
#             metadata = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:interval']
#             readings = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:IntervalReading']
#             day_start = metadata['espi:start']

#             for hourly_readings in readings:       
#                 reading_start = hourly_readings['espi:timePeriod']['espi:start']
#                 reading_value = hourly_readings['espi:value']
#                 merged_readings.append({
#                     'day (unix)': day_start,
#                     'hour (unix)': reading_start,
#                     'reading': reading_value
#                 })

#     return merged_readings

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