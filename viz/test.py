import pandas as pd

df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
                   'B': [5, 6, 7, 8, 9],
                   'C': ['a', 'b', 'c', 'd', 'e']})

df['C'].replace({
    'a': "q", 
    'b': "w", 
    'c': "e", 
    'd': "r", 
    'e': "t"
}, inplace=True)

print(df)