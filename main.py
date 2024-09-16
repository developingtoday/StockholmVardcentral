import re

import openpyxl
import requests
import streamlit as st
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io



st.title('Vardcentral in Stockholm')



@st.cache_data
def load_dynamic_data():
    base_url = "https://www.1177.se/Stockholm"
    url = st.secrets['request_url']
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


def load_data():

    data=pd.read_excel(st.secrets['url'])
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    # wb=openpyxl.load_workbook('vardcentral.xlsx')
    # urls=[]
    # for row in  wb['Sheet1'].iter_rows(min_row=2):
    #     urls.append(row[16].value)
    # # data['url']=data['url'].apply(lambda x: re.search(r'(https?://\S+)', x).group() if pd.notnull(x) else x)
    # data['url']=urls
    # data['url']=data['url'].apply(extract_url)
    return data

data_load_state = st.text('Loading data...')
data = load_dynamic_data()
df=load_data()
df=df[['hsaid','aplicat']]
res=pd.merge(data,df,on='hsaid')
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)
if st.checkbox('Show excel data'):
    st.subheader('Excel data')
    st.write(df)
optionsInput=res['aplicat'].drop_duplicates().tolist()
optionsInput.insert(0,'Toate')
option=st.selectbox('Aplicat',optionsInput)
if option=='Da':
    res=res[res['aplicat']=='Da']
if option=='Nu':
    res = res[res['aplicat'] == 'Nu']
center_lat, center_lon = 59.3293, 18.0686
m=folium.Map(location=[center_lat, center_lon], zoom_start=12)
for _, row in res.iterrows():
    folium.Marker(
        [row['latitude'], row['longitude']],
        popup=f"<a href={row['url']} target=_blank>{row['heading']}<a/> <br>Address: {row['address']}",
        icon=folium.Icon(color="green", icon="plus"),
    ).add_to(m)
st_data=st_folium(m,width=725)
