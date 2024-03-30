import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json
from datetime import datetime
import plotly.graph_objs as go
from collections import deque
import threading
import streamlit_authenticator as stauth
from st_login_form import login_form



# Page title
st.set_page_config(page_title='Fall Guard', page_icon='🤖')
st.title('Fall Guard')


#navigation bar
with st.sidebar:
    selected=option_menu(
      menu_title="Menu",
      options=["Home", "Profile","Falls","About"],
      default_index=0,

    )

#profile page

if selected =="Home":
   with st.expander('About this app'):
     st.markdown('**What can this app do?**')
     st.info('This app allow helps detect when a user falls, alerting caregivers in a timely manner.')

     st.markdown('**How to use the app?**')
     st.warning('To engage with the app, go to the sidebar and 1. Select a data set and 2. Adjust the model parameters by adjusting the various slider widgets. As a result, this would initiate the ML model building process, display the model results as well as allowing users to download the generated models and accompanying data.')

if selected == "Profile":
    st.header(f"Welcome to the {selected} page")

if selected == "Falls":

    MAX_DATA_POINTS = 1000
    UPDATE_FREQ_MS = 0.1

    time = deque(maxlen=MAX_DATA_POINTS)
    accel_x = deque(maxlen=MAX_DATA_POINTS)
    accel_y = deque(maxlen=MAX_DATA_POINTS)
    accel_z = deque(maxlen=MAX_DATA_POINTS)

    def fetch_data():
        while True:
            response = requests.post("http://tszheichoi.com/sensorlogger/data")
            data = json.loads(response.content)
            for d in data['payload']:
                if d.get("name", None) == "accelerometer":
                    ts = datetime.fromtimestamp(d["time"] / 1000000000)
                    if len(time) == 0 or ts > time[-1]:
                        time.append(ts)
                        accel_x.append(d["values"]["x"])
                        accel_y.append(d["values"]["y"])
                        accel_z.append(d["values"]["z"])

    if __name__ == "__main__":
        thread = threading.Thread(target=fetch_data)
        thread.daemon = True
        thread.start()

        st.title("Live Sensor Readings")
        st.markdown("Streamed from Sensor Logger: tszheichoi.com/sensorlogger")

        while True:
            data = [
                go.Scatter(x=list(time), y=list(d), name=name)
                for d, name in zip([accel_x, accel_y, accel_z], ["X", "Y", "Z"])
            ]
            layout = {
                "xaxis": {"type": "date"},
                "yaxis": {"title": "Acceleration ms<sup>-2</sup>"},
            }
            if len(time) > 0:
                layout["xaxis"]["range"] = [min(time), max(time)]
                layout["yaxis"]["range"] = [
                    min(accel_x + accel_y + accel_z),
                    max(accel_x + accel_y + accel_z),
                ]

            st.plotly_chart(figure={'data': data, 'layout': layout})
