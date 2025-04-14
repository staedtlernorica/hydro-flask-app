def build_viz(readings):
    from .extras import assign_historical_rates, assign_season, assign_rate_plan
    import numpy as np, datetime
    import pandas as pd

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 1000)

    df = pd.DataFrame(readings)
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    df = df.sort_values('hour (unix)')

    df['day (unix)'] = pd.to_numeric(df['day (unix)'])
    df['hour (unix)'] = pd.to_numeric(df['hour (unix)'])
    df['reading'] = pd.to_numeric(df['reading'])/1000000
    df.rename(columns={'reading': 'usage (kWh)'}, inplace=True)
    # df['datetime (UTC)'] = pd.to_datetime(df['hour (unix)'],unit='s', utc=True).dt.tz_convert('UTC')
    # df['date (UTC)'] = pd.to_datetime(df['hour (unix)'],unit='s').dt.date
    # df['hour (UTC)'] = pd.to_datetime(df['hour (unix)'],unit='s').dt.hour
    # df['datetime (ET)'] = pd.to_datetime(df['hour (unix)'],unit='s', utc=True).dt.tz_convert('America/New_York')
    df['date (ET)'] = pd.to_datetime(df['hour (unix)'], unit='s', utc=True).dt.tz_convert('America/New_York').dt.date
    df['hour (ET)'] = pd.to_datetime(df['hour (unix)'], unit='s', utc=True).dt.tz_convert('America/New_York').dt.hour
    df['weekend'] = pd.to_datetime(df['hour (unix)'], unit='s', utc=True).dt.tz_convert('America/New_York').dt.day_of_week
    df['weekend'] = np.where(df['weekend'] < 5, False, True)
   
    # get list of holiday dates to create a holiday column, as holidays affect TOU and ULO rates
    import holidays
    earliest_year = df['date (ET)'].min().year
    latest_year = df['date (ET)'].max().year
    years_in_df = list(range(earliest_year,latest_year + 1))
    holiday_dates = [date for date, name in holidays.country_holidays('CA', subdiv='ON', years=years_in_df).items()]

    # https://stackoverflow.com/a/72793101/6030118; add Civic Day as 'holidays' module doesn't support it
    civic_holidays = [np.busday_offset(f'{year}-08', 0, roll='forward', weekmask='Mon') for year in years_in_df]
    holiday_dates.extend(civic_holidays)

    df['holiday'] = (df['date (ET)'].isin(holiday_dates))
    move_col = df.pop('usage (kWh)')
    df.insert(len(df.columns), 'usage (kWh)', move_col)         # re-arrange for better readability in upcoming dataframes
   
    # assign TOU and ULO plans and their rates to each hourly reading
    from .oeb_rates import oeb_rates

    df_tou = df.copy(deep = True)
    tou_dates = list(oeb_rates['tou'].keys())
    df_tou['Plan'] = 'TOU'
    df_tou['Rates Period'] = assign_historical_rates(df_tou['date (ET)'], tou_dates)
    df_tou['Rates Plan'] = df_tou['Rates Period'].map(oeb_rates['tou'])
    tou_rates = [0,1,2]
    df_tou['TOU Season'] = df_tou['date (ET)'].map(assign_season) #mid/on-peak price period switches on May 1/Nov 1
    tou_conditions = [
        (df_tou['holiday'] == True) | 
        (df_tou['weekend'] == True) | 
        df_tou['hour (ET)'].isin([19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]),
        (df_tou['TOU Season'] == 'summer') & (df_tou['hour (ET)'].isin([7, 8, 9, 10, 17, 18])) | 
        (df_tou['TOU Season'] == 'winter') & (df_tou['hour (ET)'].isin([11, 12, 13, 14, 15, 16])),
        (df_tou['TOU Season'] == 'winter') & (df_tou['hour (ET)'].isin([7, 8, 9, 10, 17, 18])) | 
        (df_tou['TOU Season'] == 'summer') & (df_tou['hour (ET)'].isin([11, 12, 13, 14, 15, 16]))
    ]
    df_tou['Price Period'] = np.select(tou_conditions, tou_rates, default=np.nan)
    df_tou['Rate (c)'] = df_tou.apply(lambda row: row['Rates Plan'][int(row['Price Period'])] 
                            if pd.notna(row['Rates Plan']) else np.nan, axis=1)
    df_tou['Prices (c)'] = df_tou[["Rate (c)"]].multiply(df_tou["usage (kWh)"], axis="index").round(2)

    #convert 0/1/2 to off-peak/mid-peak/on-peak for readability
    df_tou['Price Period'] = np.select([df_tou['Price Period'] == 0, 
                                            df_tou['Price Period'] == 1, 
                                            df_tou['Price Period'] == 2], 
                                            ['tou: off-peak', 
                                            'tou: mid-peak', 
                                            'tou: on-peak'], 
                                            default = np.array(np.nan, dtype='object'))   

    df_ulo = df.copy(deep=True)
    df_ulo = df_ulo[df_ulo['date (ET)'] >= datetime.date(2023, 5, 1)] #ULO rates only took effect on May 1, 2023
    ulo_dates = list(oeb_rates['ulo'].keys())
    df_ulo['Plan'] = 'ULO'
    df_ulo['Rates Period'] = assign_historical_rates(df_ulo['date (ET)'], ulo_dates)
    df_ulo['Rates Plan'] = df_ulo['Rates Period'].map(oeb_rates['ulo'])
    ulo_rates = [0,1,2,3]
    ulo_conditions = [
        df_ulo['hour (ET)'].isin([23, 0, 1, 2, 3, 4, 5, 6]), 
        (df_ulo['weekend'] == True) & (df_ulo['hour (ET)'].isin(range(7, 23))) | 
        (df_ulo['holiday'] == True) & (df_ulo['hour (ET)'].isin(range(7, 23))),
        df_ulo['hour (ET)'].isin([7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 21, 22, 23]),
        df_ulo['hour (ET)'].isin([16, 17, 18, 19, 20])    
    ]
    df_ulo['Price Period'] = np.select(ulo_conditions, ulo_rates, default=np.nan)
    df_ulo['Rate (c)'] = df_ulo.apply(lambda row: row['Rates Plan'][int(row['Price Period'])] 
                            if pd.notna(row['Rates Plan']) else np.nan,
                            axis=1)
    df_ulo['Prices (c)'] = df_ulo[["Rate (c)"]].multiply(df_ulo["usage (kWh)"], axis="index").round(2)

    #convert 0/1/2/3 to ultra-low/off-peak/mid-peak/on-peak for readability
    df_ulo['Price Period'] = np.select([df_ulo['Price Period'] == 0, 
                                            df_ulo['Price Period'] == 1, 
                                            df_ulo['Price Period'] == 2, 
                                            df_ulo['Price Period'] == 3], 
                                            ['ulo: ultra-low', 
                                            'ulo: off-peak', 
                                            'ulo: mid-peak', 
                                            'ulo: on-peak'], 
                                            default = np.array(np.nan, dtype='object'))    
    
    # import nest_asyncio
    # nest_asyncio.apply()

    import datetime

    df_tr = df.copy(deep=True)
    tr_dates = list(oeb_rates['tr'].keys())
    tr_plan = oeb_rates['tr']

    df_tr['Plan'] = 'TR'
    df_tr['Rates Period'] = df_tr['date (ET)'].apply(lambda x: assign_rate_plan(x, tr_dates))
    df_tr['Cumulative Usage (kWh)'] = df_tr.groupby([pd.to_datetime(df_tr['date (ET)']).dt.year, 
                                    pd.to_datetime(df_tr['date (ET)']).dt.month])['usage (kWh)'].cumsum()

    df_tr['Rates Plan'] = df_tr['Rates Period'].apply(lambda x: tr_plan[x]['prices'] 
                                        if pd.notna(x) else np.nan)
    df_tr['TR Threshold'] = df_tr['Rates Period'].apply(lambda x: tr_plan[x]['threshold'] 
                                        if pd.notna(x) else np.nan)
    df_tr['Price Period'] = np.where(df_tr['Cumulative Usage (kWh)'] <= df_tr['TR Threshold'], 'tr: lower', 'tr: higher')
    df_tr['Rate (c)'] = df_tr.apply(lambda x: x['Rates Plan'][0] if x['Cumulative Usage (kWh)'] < x['TR Threshold'] else x['Rates Plan'][1], axis=1)
    df_tr['Prices (c)'] = df_tr[["Rate (c)"]].multiply(df_tr["usage (kWh)"], axis="index").round(2)

    df_tr.insert(len(df_tr.columns) - 1, 'Cumulative Usage (kWh)', df_tr.pop('Cumulative Usage (kWh)'))
    df_tr.insert(len(df_tr.columns) - 1, 'TR Threshold', df_tr.pop('TR Threshold'))

    # longer method but more explicit/clear
    # find id of rows where starting cumulative usages < threshold AND ending cumulative usage > above threshold, ie where readings 
    # started with a lower rate but crosses the TR threshold and ends with a higher rate; then split those readings into two rows: 
    # - one where ending cumulative usage ends at the threshold (with the lower TR rate)
    # - one where starting cumulative usage starts at the threshold (with the higher TR rate)
    # then re-insert the duplicated rows back into the df_tr, replacing the original crossover readings
    cumu_usages = pd.DataFrame({'date': df_tr['date (ET)'],
                                'starting cumulative usage': df_tr['Cumulative Usage (kWh)'] - df_tr['usage (kWh)'], 
                                'ending cumulative usage': df_tr['Cumulative Usage (kWh)'], 
                                'threshold': df_tr['TR Threshold']})

    crossover_readings = ((cumu_usages[(cumu_usages['starting cumulative usage'] < cumu_usages['threshold']) &
                    (cumu_usages['ending cumulative usage'] > cumu_usages['threshold'])])
                    .groupby([pd.to_datetime(cumu_usages['date']).dt.year,
                                pd.to_datetime(cumu_usages['date']).dt.month])
                    .idxmin())

    crossover_readings_id = (crossover_readings['starting cumulative usage'].to_list())
    crossover_readings = df_tr.loc[crossover_readings_id]

    df_tr = df_tr.reindex(df_tr.index.append(df_tr.index[crossover_readings_id]))
    df_tr = df_tr.sort_index().reset_index(drop=True)

    # assign vars together before the index for higher_crossover is modified and no longer exists
    lower_crossover_index = df_tr[df_tr.duplicated(keep='last') == True].index      #get index of lower threshold duplicated rows
    lower_crossover = df_tr.iloc[lower_crossover_index]                             #copy lower threshold duplicated rows
    higher_crossover_index = df_tr[df_tr.duplicated(keep='first') == True].index    #get index of higher threshold duplicated rows
    higher_crossover = df_tr.iloc[higher_crossover_index]                           #copy higher threshold duplicated rows

    lower_crossover['usage (kWh)'] = lower_crossover['usage (kWh)'] - (lower_crossover['Cumulative Usage (kWh)'] - lower_crossover['TR Threshold'])
    lower_crossover['Cumulative Usage (kWh)'] = lower_crossover['TR Threshold']
    lower_crossover['Rate (c)'] = lower_crossover['Rates Plan'].apply(lambda x: x[0])
    lower_crossover['Prices (c)'] = lower_crossover[["Rate (c)"]].multiply(lower_crossover["usage (kWh)"], axis="index").round(2)
    lower_crossover['Price Period'] = 'tr: lower'
    df_tr.iloc[lower_crossover_index] = lower_crossover     

    higher_crossover['usage (kWh)'] = higher_crossover['Cumulative Usage (kWh)'] - higher_crossover['TR Threshold']
    higher_crossover['Rate (c)'] = higher_crossover['Rates Plan'].apply(lambda x: x[1])
    higher_crossover['Prices (c)'] = higher_crossover[["Rate (c)"]].multiply(higher_crossover["usage (kWh)"], axis="index").round(2)
    higher_crossover['Price Period'] = 'tr: higher'
    df_tr.iloc[higher_crossover_index] = higher_crossover
    # print(crossover_readings)
    # print(lower_crossover_index, higher_crossover_index)
    # print(lower_crossover)
    # print(higher_crossover)


    dfa = pd.concat([df_ulo, df_tou], axis=0)
    dfa = dfa.sort_values(['date (ET)', 'hour (ET)'])
    dfa.reset_index(drop=True, inplace=True)  #reset the index from 1,1,2,2 ... to 1,2,...

    dfa['Cumulative Usage (kWh)'] = dfa.groupby([pd.to_datetime(dfa['date (ET)']).dt.year, 
                                            pd.to_datetime(dfa['date (ET)']).dt.month,
                                            dfa['Plan']])['usage (kWh)'].cumsum()

    dfa = pd.concat([dfa, df_tr], axis=0)
    dfa.sort_values(['Plan', 'date (ET)', 'hour (ET)'], inplace=True)
    dfa.reset_index(drop=True, inplace=True)  #reset the index from 1,1,2,2 ... to 1,2,...

    dfa['Prices (c)'] = (dfa['Prices (c)']/100).round(2)
    dfa.rename(columns={'Prices (c)': 'Prices ($)'}, inplace=True)
    test = dfa[dfa['date (ET)'] >= datetime.date(2024, 7, 1)]
    test = dfa[dfa['date (ET)'] <= datetime.date(2024, 7, 31)]
    test.reset_index(drop=True, inplace=True)
    # test = test[test['date (ET)'] == datetime.date(2023, 7, 3)]


    import plotly.express as px

    testa = test[(test['date (ET)'] >= datetime.date(2024, 7, 1)) & 
                (test['date (ET)'] <= datetime.date(2024, 7, 31))]

    col_scheme_1 = ["#0aceff", "#0a7cff", "#0230e8", "#d18feb", "#b057d4", "#8aa3b8", "#bac2bc", "#4b4d4b","#282928"]
    col_scheme_2 = ['#41ff70', '#fcff39', '#d85521', '#8503ff', '#2d037c', '#0cede6', '#1eb73a', '#ffd51a', '#ff0000'] 
    alt_scheme = ["teal", "green", "olive", "#F17FB7", "#D14081", "#8BDAE4", "#2E96F0", "#0173FF", "#1E1B76"]
    placeholder_scheme = ["", "", "", "", "", "", "", "", ""]
    # Create a side-by-side bar chart
    fig = px.histogram(testa, 
                    x='Plan', 
                    y='Prices ($)', 
                    facet_col='date (ET)', 
                    facet_col_spacing=0.0155, 
                    color='Price Period', 
                    color_discrete_sequence = col_scheme_1,
                    barmode='stack',  
                    labels = {'Plan': ''},  # got from https://stackoverflow.com/a/63439845/6030118
                    width=1400,
                    height=450
                    )
    # fig.show()

    # fig.update_xaxes(dict(showticklabels=False))
    # fig.update_xaxes(dict(showticklabels=False, showticksuffix='none', showtickprefix='none'))
    # fig.update_xaxes(showticksuffix='none')
    # fig.update_xaxes(showtickprefix='none')
    fig.update_xaxes(showticklabels=False)
    fig.for_each_annotation(lambda a: a.update(text= '-'.join(a.text.split("=")[-1].split('-')[::-1])))   # change date (ET)='yyyy-mm-dd' to 'dd-mm-yyyy'
    fig.update_annotations(dict(xshift=20, yshift=-380, textangle=55))
    # fig.for_each_annotation(lambda a: print(dir(a)))
    # fig.for_each_annotation(lambda a: print(type(a)))

    fig.update_layout(
        yaxis_title='Sum of Daily Prices ($)',
        # xaxis_title_standoff=90,
    )

    fig.update_layout(
                title={
                'text' : 'Energy Plans Price Comparison',
                'x':0.5,
                'y':0.985,
                'yanchor': "top",
                'xanchor': "center",  
            })

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        # xanchor="left",
        # x=-1
    ))

    fig.update_layout({
        'plot_bgcolor': '#f0f0f0',
        'paper_bgcolor': '#f0f0f0',
    })
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    config = {'displayModeBar': False}

    # fig.show(config = config)

    # print(fig.layout.width)

    return fig.to_html(full_html=False)

    # fig = px.histogram(testa, x=testa['date (ET)'], y='Prices ($)', color='Price Period', barmode='group',)
    # fig.show()


    # fig = px.histogram(testa, x=testa['date (ET)'], y='Prices ($)', color='Price Period', barmode='group', histfunc='sum')
    # fig.show()    


if __name__ == "__main__":
    # build_viz()
    import os, xmltodict
    from extras import merge_readings


    print()
    files = (os.listdir('./static/files/'))

    xml_files = []

    for i in files:
        with open(f'./static/files/{i}') as xml_file:

            # print(f'./static/files/{i}')

            data_dict = xmltodict.parse(xml_file.read())
            xml_files.append(data_dict)

    # print(xml_files)
    # y = merge_readings(os.getcwd())
    # os.chdir('../..')
    # print(os.curdir)
    x = build_viz(xml_files)


    pass