import xmltodict, pandas as pd, numpy as np

with open('test.XML', 'r', encoding='utf-8') as file:
    xml_content = file.read()
data_dict = xmltodict.parse(xml_content)
file.close()

all = []
for i in range(4, len(data_dict['feed']['entry'])):
    readings = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:IntervalReading']
    for hourly_readings in readings:       
        all.append(int(hourly_readings['espi:value']))

s = pd.Series(all)
distribution = s.value_counts(normalize=True).sort_index()
for i in range(4, len(data_dict['feed']['entry'])):
    readings = data_dict['feed']['entry'][i]['content']['espi:IntervalBlock']['espi:IntervalReading']
    for hourly_readings in readings:       
        hourly_readings['espi:value'] = np.random.choice(distribution.index, size=1, p=distribution.values)

test = (xmltodict.unparse(data_dict, pretty=True))
with open('output.xml', 'w', encoding='utf-8') as f:
    f.write(test)