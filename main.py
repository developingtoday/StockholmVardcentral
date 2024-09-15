import re

import openpyxl
import requests
import streamlit as st
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium

st.title('Vardcentral in Stockholm')



@st.cache_data
def load_dynamic_data():
    base_url = "https://www.1177.se/Stockholm"
    url = "https://www.1177.se/api/hjv/search?st=49d6e0b2-1e69-40f9-998e-490cf31722c3&nearby=false&s=distance&g=ChIJywtkGTF2X0YRZnedZ9MnDag&lat=&lng=&location=Stockholm%20kommun&caretype=V%C3%A5rdcentral&q=&p=1&componentname=&batchsize=100&sortorder=distance"
    response = requests.get(url)
    df=pd.DataFrame.empty
    if response.status_code==200:
        data=response.json()
        df=pd.DataFrame(data['SearchHits'])
        df['Url'] = df['Url'].apply(lambda x: f'{base_url}{x}')
        lowercase = lambda x: str(x).lower()
        df.rename(lowercase, axis='columns', inplace=True)
    return df

def extract_url(hyperlink):
    match = re.search(r'HYPERLINK\("([^"]+)"', hyperlink)
    return match.group(1) if match else None

@st.cache_data
def load_data():
    data = pd.read_excel('vardcentral.xlsx', engine='openpyxl',engine_kwargs ={'keep_links':True})
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    wb=openpyxl.load_workbook('vardcentral.xlsx')
    urls=[]
    for row in  wb['Sheet1'].iter_rows(min_row=2):
        urls.append(row[16].value)
    # data['url']=data['url'].apply(lambda x: re.search(r'(https?://\S+)', x).group() if pd.notnull(x) else x)
    data['url']=urls
    data['url']=data['url'].apply(extract_url)
    return data

data_load_state = st.text('Loading data...')
data = load_dynamic_data()
df=load_data()
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)
if st.checkbox('Show excel data'):
    st.subheader('Excel data')
    st.write(df)

center_lat, center_lon = 59.3293, 18.0686
m=folium.Map(location=[center_lat, center_lon], zoom_start=12)
for _, row in data.iterrows():
    folium.Marker(
        [row['latitude'], row['longitude']],
        popup=f"<a href={row['url']} target=_blank>{row['heading']}<a/> <br>Address: {row['address']}",
        icon=folium.Icon(color="green", icon="plus"),
    ).add_to(m)
st_data=st_folium(m,width=725)
