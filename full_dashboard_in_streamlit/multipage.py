import streamlit as st
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import json
from hugchat import hugchat
from hugchat.login import Login

def homePage():
    st.title("Homepage")

def earthquake():
    st.title("Earthquake")
    col1,col2 = st.columns(2)

    default_params = {
    'format': 'geojson',  # Default format
    'starttime': '2023-01-01',  # Default starttime
    'latitude': 37.871960,  # Default latitude
    'longitude': -122.259094,  # Default longitude
    'maxradiuskm': 100,  # Default maxradiuskm
    'orderby': 'time',  # Default orderby
    'minmagnitude': 0.0  # Default minmagnitude
    }

    format_param = col1.text_input("Enter the format (e.g., geojson):")
    starttime_param = col1.text_input("Enter the start time (e.g., 2023-01-01):")
    maxradiuskm_param = col1.number_input("Enter the max radius in kilometers (e.g., 100):")
    orderby_param = col1.text_input("Enter the order (e.g., magnitude):")
    minmagnitude_param = col1.number_input("Enter the minimum magnitude (e.g., 2):")



    custom_params = {
        'format': format_param,
        'starttime': starttime_param,
        'latitude': 37.871960,
        'longitude': -122.259094,
        'maxradiuskm': maxradiuskm_param,
        'orderby': orderby_param,
        'minmagnitude': minmagnitude_param
    }

    params = default_params.copy()
# params.update(custom_params)

    base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    response = requests.get(base_url, params=params)
    data = response.json()
    coordinates_list = [(feature["geometry"]["coordinates"][1], feature["geometry"]["coordinates"][0]) for feature in data["features"]]
    df = pd.DataFrame(coordinates_list, columns=['lat', 'lon'])
    col2.map(df)
    col2.write(coordinates_list)
    


def smartcover():
    st.title("Smartcover")
    col1,col2 = st.columns(2)
    # variable to store the JWT token
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX3BrIjoiMTE1MjkiLCJpYXQiOjE2OTQwOTQ5OTIsImV4cCI6MTcyNTcxNzM5Mn0.K5lQTxGmkyMJtZXgB3pReJyXF1yAxlYSUzlcM1B9QOw'
    # set the authorization header
    headers = {'Authorization': 'Bearer ' + token} # set the request parameters

    # make the GET request
    ll_response = requests.get('https://www.mysmartcover.com/api/locations/list.php',headers=headers)
    ll_data = ll_response.json()
    coordinates_list = [(location['latitude'], location["longitude"]) for location in ll_data["locations"]]
    df = pd.DataFrame(coordinates_list, columns=['lat', 'lon'])
    col1.map(df)
    col1.write(ll_data)
    

    hd_params = {'location': 22375,
          'start_time': '2022-12-31 23:59:59',
          'end_time': '2023-1-31 23:59:59',
          'data_type': '3'}
    hd_response = requests.get('https://www.mysmartcover.com/api/locations/data.php',params=hd_params,headers=headers)
    hd_data = hd_response.json()
    col2.header("Historical Data ID: 22375")
    col2.write(hd_data)

def greenIndex():
    st.title("Green Index")

def building():
    st.title("Building Model")
    

def main():
    st.set_page_config(layout="wide")
    hf_email =""
    hf_pass =""
    with st.sidebar:
        st.title("Navigation")
        page = st.sidebar.selectbox("Select a page", ["Home","Earthquake","Smartcover","Green Index","Building Model","Chatbot"])
        st.button("Sign Out")
        if ('EMAIL' in st.secrets) and ('PASS' in st.secrets):
            st.success('HuggingFace Login credentials already provided!', icon='✅')
            hf_email = st.secrets['EMAIL']
            hf_pass = st.secrets['PASS']
        else:
            hf_email = st.text_input('Enter E-mail:', type='password')
            hf_pass = st.text_input('Enter password:', type='password')
        if not (hf_email and hf_pass):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
        # Store LLM generated responses

    if page == "Home":
        homePage()
    elif page == "Earthquake":
        earthquake()
    elif page == "Smartcover":
        smartcover()
    elif page == "Green Index":
        greenIndex()
    elif page == "Building Model":
        building()
    elif page == "Chatbot":
        chatbot()
    
    
def chatbot():
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Function for generating LLM response
    def generate_response(prompt_input, email, passwd):
        # Hugging Face Login
        sign = Login(email, passwd)
        cookies = sign.login()
        # Create ChatBot                        
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        return chatbot.chat(prompt_input)

# User-provided prompt
    hf_email = st.secrets['EMAIL']
    hf_pass = st.secrets['PASS']
    if prompt := st.chat_input(disabled=not (hf_email and hf_pass)):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

# Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt, hf_email, hf_pass) 
                st.write(response) 
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
    
if __name__ == "__main__":
    main()