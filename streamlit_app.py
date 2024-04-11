import streamlit as st
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import gspread
import pandas as pd
import numpy as np
import csv

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

    # Menu
    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    username = None #initialize username 
    password_matched = False

    if choice == "Home":
        st.subheader("Home")
        with st.expander('About this app'):
            st.markdown('**What can this app do?**')
            st.info('This app allows helps detect when a user falls, alerting caregivers in a timely manner.')

            st.markdown('**How to use the app?**')
            st.warning('To engage with the app,')

    elif choice == "SignUp":
        st.subheader("Create New Account")
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Fetch existing data
        existing_data = conn.read(worksheet="Data", usecols=list(range(6)), ttl=5 )
        existing_data = existing_data.dropna(how="all")
        with st.form(key="info"):
            first_name = st.text_input(label="First Name")
            last_name = st.text_input(label="Last Name")
            new_password = st.text_input("Password", type='password')
            birthdate = st.text_input(label="Birthday (MM/DD/YYYY)")
            new_email_address = st.text_input(label="Email Address")
            submit_button = st.form_submit_button(label="Submit User Information")

        if submit_button:  # creates new row of data when button is clicked
            user_data = pd.DataFrame([
                {"First Name": first_name,
                 "Last Name": last_name,
                 "Birthday": birthdate,
                 "Password": new_password,
                 "Email": new_email_address,
                 "Falls": "False"}
            ])
            updated_df = pd.concat([existing_data, user_data], ignore_index=True)
            # Update Google Sheets
            conn.update(worksheet="Data", data=updated_df)
            st.success("You have successfully created an account")
            st.info("Go to Login menu to login")
        
    elif choice == "Login":
        st.subheader("Login")
        username = st.sidebar.text_input("Name")
        password = st.sidebar.text_input("Password (letters only)", type='password')
        conn = st.connection("gsheets", type=GSheetsConnection)
        signup_data = conn.read(worksheet="Data", ttl=5)
        password_matched = False  # Initialize the variable to track if password matched
        
        #st.write("Signup data:", signup_data)  # Debug statement to check signup_data
        
        if st.sidebar.checkbox("Login"):
            for _, row in signup_data.iterrows():  # Iterate over DataFrame rows using iterrows()
                #st.write("Row:", row)  # Debug statement to check each row
                if row["First Name"] == username and row["Password"] == password:
                    st.success("Logged in as {}".format(username))
                    task = st.sidebar.selectbox("User Menu", ["Profile", "Data", "Falls"])
                    password_matched = True
                    if choice == "Data":
                        st.subheader("Falls")
                        # Fall detection logic
                        sum_vector_f = []
                        test_size = 40

                        with open('/Users/mochi/Desktop/fall1.csv', 'r') as f:
                            reader = csv.reader(f)
                            data = list(reader)
                        data_array = np.array(data)
                        sum_vector = data_array[:, 6]
                        length1 = sum_vector.size

                        for item in sum_vector:
                            temp = float(item)
                            sum_vector_f.append(temp)

                        max_value = np.max(np.abs(sum_vector_f))
                        threshold1 = max_value / 4
                        threshold2 = max_value / 2

                        sample_size = int(length1 / test_size)
                        sample_array = np.zeros((sample_size, test_size))
                        target_array = []

                        for item in range(sample_size):
                            temp1 = sum_vector_f[item * test_size: (item + 1) * test_size]
                            sample_array[item][:] = temp1
                            temp2 = sum(np.abs(temp1)) / test_size

                            if temp2 >= threshold2:
                                target_array.append(-1)
                            elif temp2 > threshold1:
                                target_array.append(1)
                            else:
                                target_array.append(-1)

                        # Update Google Sheets if fall is detected
                        if any(target_array):
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            fall_data = conn.read(worksheet="Data", ttl=5)  # Import the whole sheet
                            headers = fall_data.columns.tolist()

                            # Find the index of "First Name" and "Fall" columns
                            first_name_index = headers.index("First Name")
                            fall_index = headers.index("Fall")

                            for i, row in fall_data.iterrows():
                                if row["First Name"] == username:  # Match the first name with the inputted first name during login
                                    fall_data.at[i, "Fall"] = "True" if any(target_array) else "False"  # Set "True" if fall is detected, else "False"
                                    conn.update(worksheet="Data", data=fall_data)  # Update the Google Sheet
                                    st.success("Fall detected! Updated Google Sheet.")
                                    break
                    break
                    if choice == "Falls":
                        server = Flask(__name__)
                        app = dash.Dash(__name__, server=server)

                        MAX_DATA_POINTS = 1000
                        UPDATE_FREQ_MS = 100

                        time = deque(maxlen=MAX_DATA_POINTS)
                        accel_x = deque(maxlen=MAX_DATA_POINTS)
                        accel_y = deque(maxlen=MAX_DATA_POINTS)
                        accel_z = deque(maxlen=MAX_DATA_POINTS)

                        app.layout = html.Div(
                            [
                                dcc.Markdown(
                                    children="""
                                    # Live Sensor Readings
                                    Streamed from Sensor Logger: tszheichoi.com/sensorlogger
                                """
                                ),
                                dcc.Graph(id="live_graph"),
                                dcc.Interval(id="counter", interval=UPDATE_FREQ_MS),
                            ]
                        )


                        @app.callback(Output("live_graph", "figure"), Input("counter", "n_intervals"))
                        def update_graph(_counter):
                            data = [
                                go.Scatter(x=list(time), y=list(d), name=name)
                                for d, name in zip([accel_x, accel_y, accel_z], ["X", "Y", "Z"])
                            ]

                            graph = {
                                "data": data,
                                "layout": go.Layout(
                                    {
                                        "xaxis": {"type": "date"},
                                        "yaxis": {"title": "Acceleration ms<sup>-2</sup>"},
                                    }
                                ),
                            }
                            if (
                                len(time) > 0
                            ):  #  cannot adjust plot ranges until there is at least one data point
                                graph["layout"]["xaxis"]["range"] = [min(time), max(time)]
                                graph["layout"]["yaxis"]["range"] = [
                                    min(accel_x + accel_y + accel_z),
                                    max(accel_x + accel_y + accel_z),
                                ]

                            return graph


                        @server.route("/data", methods=["POST"])
                        def data():  # listens to the data streamed from the sensor logger
                            if str(request.method) == "POST":
                                print(f'received data: {request.data}')
                                data = json.loads(request.data)
                                for d in data['payload']:
                                    if (
                                        d.get("name", None) == "accelerometer"
                                    ):  #  modify to access different sensors
                                        ts = datetime.fromtimestamp(d["time"] / 1000000000)
                                        if len(time) == 0 or ts > time[-1]:
                                            time.append(ts)
                                            # modify the following based on which sensor is accessed, log the raw json for guidance
                                            accel_x.append(d["values"]["x"])
                                            accel_y.append(d["values"]["y"])
                                            accel_z.append(d["values"]["z"])
                            return "success"

            if not password_matched:
                st.warning("Incorrect Name/Password.")
                

if __name__ == '__main__':
    main()
