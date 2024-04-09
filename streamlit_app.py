import streamlit as st
#from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import dash
from dash.dependencies import Output, Input
from dash import dcc, html, dcc
from datetime import datetime
import json
import plotly.graph_objs as go
from collections import deque
from flask import Flask, request



def main():
# Page title
    st.set_page_config(page_title='Fall Guard', page_icon='🤖')
    st.title('Fall Guard')
    #menu
    menu = ["Home", "Login", "SignUp", "About", "Falls"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        with st.expander('About this app'):
            st.markdown('**What can this app do?**')
            st.info('This app allow helps detect when a user falls, alerting caregivers in a timely manner.')

            st.markdown('**How to use the app?**')
            st.warning('To engage with the app,')

    elif choice =="SignUp":
        st.subheader("Create New Account")
        conn = st.connection("gsheets", type=GSheetsConnection)
        #fetch existing data
        existing_data = conn.read(worksheet = "Data", usecols=list(range(4)), ttl = 5)
        existing_data = existing_data.dropna(how="all")
        with st.form(key = "info"):
            first_name = st.text_input(label="First Name")
            last_name = st.text_input(label="Last Name")
            new_password = st.text_input("Password", type='password')
            birthdate = st.text_input(label="Birthday (MM/DD/YYYY)")
            email_address = st.text_input(label="Email Address")
            submit_button = st.form_submit_button(label = "Submit User Information")
        
        
        if submit_button: #creates new row of data when button is clicked
            user_data = pd.DataFrame(
                [
                    {"First Name": first_name,
                    "Last Name": last_name,
                    "Birthday": birthdate,
                    "Password": new_password,
                    "Email": email_address
                    }
                ]
            )
            updated_df = pd.concat([existing_data, user_data], ignore_index=True)
            #update google sheets
            conn.update(worksheet="Data", data=updated_df)
            st.success("You have successfully created an account")
            st.info("Go to Login menu to login")

        password_data = pd.DataFrame(
                [
                    {"Person": first_name,
                     "Credential": new_password}
                ]
            )
            
    elif choice == "Login":
        st.subheader("Login")
        username = st.sidebar.text_input("Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login"):
            if (password == "123"):
                st.success("Logged in as {}".format(username))
                task = st.sidebar.selectbox("User Menu",["Profile", "Data"])
                if task == "Profile":
                    st.subheader("Welcome {}".format(username))

                elif task == "Data":
                    st.subheader("Data")
                    
            else:
                st.warning("Incorrect Name/Password, Click Sign Up to create an account")
                
    






if __name__ == '__main__':
    main()