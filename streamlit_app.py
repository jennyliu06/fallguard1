import streamlit as st
#from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import sqlite3
from streamlit_gsheets import GSheetsConnection
import pandas as pd
conn = sqlite3.connect('data.db')
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS usertable(username TEXT,password TEXT,email TEXT)')

def add_userdata(username,password,email):
    c.execute('INSERT INTO usertable(username,password,email) VALUES (?,?,?)', (username,password,email))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM usertable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data

def view_all_users():
    c.execute('SELECT * FROM usertable')
    data = c.fetchall()
    return data
    


def main():
# Page title
    st.set_page_config(page_title='Fall Guard', page_icon='🤖')
    st.title('Fall Guard')

    #menu
    menu = ["Home", "Login", "SignUp", "Create Account", "About", "Falls"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        with st.expander('About this app'):
            st.markdown('**What can this app do?**')
            st.info('This app allow helps detect when a user falls, alerting caregivers in a timely manner.')

            st.markdown('**How to use the app?**')
            st.warning('To engage with the app, go to the sidebar and 1. Select a data set and 2. Adjust the model parameters by adjusting the various slider widgets. As a result, this would initiate the ML model building process, display the model results as well as allowing users to download the generated models and accompanying data.')

    elif choice == "Login":
        st.subheader("Login")
 
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            result = login_user(username,password)
            
            if result:
                st.success("Logged in as {}".format(username))

                task = st.sidebar.selectbox("User Menu",["Profile", "Data"])
                if task == "Profile":
                    st.subheader("Welcome {}".format(username))

                elif task == "Data":
                    st.subheader("Data")
                else:
                    st.warning("Incorrect Username/Password")

    elif choice =="SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        new_email = st.text_input("Email")

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user, new_password, new_email)
            st.success("You have successfully created an account")
            st.info("Go to Login menu to login")
    
    elif choice =="Create Account":
        st.subheader("Create account with contact information")
        #establishing a google sheets connection
        conn = st.connection("gsheets", type=GSheetsConnection)
        #fetch existing data
        existing_data = conn.read(worksheet = "Fall Guard", usecols=list(range(3)), ttl = 5)
        existing_data = existing_data.dropna(how="all")

        with st.form(key = "login"):
            first_name = st.text_input(label="First Name")
            last_name = st.text_input(label="Last Name")
            email_address = st.text_input(label="Email Address")


if __name__ == '__main__':
    main()