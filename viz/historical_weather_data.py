import asyncio
import platform
if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from env_canada import ECHistoricalRange
def get_historical_weather(first_time, latest_time):

    ec = ECHistoricalRange(station_id=int(31688), timeframe="hourly",
                        daterange=(first_time, latest_time))
    x = ec.get_data()
    return x

# print(stations.iloc[0,0])
# ec.df.to_csv('weather_data.csv', index=True)