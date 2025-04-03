import numpy as np, datetime
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)
import extras as ex

df = pd.DataFrame(ex.merge_readings())
df = df.drop_duplicates()
df = df.reset_index(drop=True)