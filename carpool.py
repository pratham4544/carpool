import streamlit as st
import pandas as pd
import sqlite3

# Create or connect to SQLite database
conn = sqlite3.connect('rides.db')
c = conn.cursor()

# Create rides table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS rides
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             time TEXT, 
             start_destination TEXT, 
             end_destination TEXT, 
             fare REAL, 
             seats INTEGER, 
             contact_number TEXT)''')
conn.commit()

# Create passenger requests table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS passenger_requests
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             time TEXT, 
             start_destination TEXT, 
             end_destination TEXT, 
             contact_number TEXT)''')
conn.commit()

# Create messages table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             sender TEXT, 
             receiver TEXT,
             message TEXT)''')
conn.commit()

# Function to add a new ride to the database
def add_ride(time, start_destination, end_destination, fare, seats, contact_number):
    c.execute('''INSERT INTO rides (time, start_destination, end_destination, fare, seats, contact_number) 
                 VALUES (?, ?, ?, ?, ?, ?)''', (time, start_destination, end_destination, fare, seats, contact_number))
    conn.commit()

# Function to retrieve all rides from the database
def get_rides():
    c.execute('''SELECT * FROM rides''')
    rides = c.fetchall()
    return pd.DataFrame(rides, columns=["ID", "Time", "Start Destination", "End Destination", "Fare", "Seats", "Contact Number"])

# Function to add a new passenger request to the database
def add_passenger_request(time, start_destination, end_destination, contact_number):
    c.execute('''INSERT INTO passenger_requests (time, start_destination, end_destination, contact_number) 
                 VALUES (?, ?, ?, ?)''', (time, start_destination, end_destination, contact_number))
    conn.commit()

# Function to retrieve all passenger requests from the database
def get_passenger_requests():
    c.execute('''SELECT * FROM passenger_requests''')
    requests = c.fetchall()
    return pd.DataFrame(requests, columns=["ID", "Time", "Start Destination", "End Destination", "Contact Number"])

# Function to add a message to the database
def add_message(sender, receiver, message):
    c.execute('''INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)''', (sender, receiver, message))
    conn.commit()

# Function to retrieve messages between two users
def get_messages(sender, receiver):
    c.execute('''SELECT * FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)''',
              (sender, receiver, receiver, sender))
    messages = c.fetchall()
    return pd.DataFrame(messages, columns=["ID", "Sender", "Receiver", "Message"])

# Page layout
st.set_page_config(layout="wide")

# Title and navigation
st.title("Carpooling Website")
menu = st.sidebar.radio("Navigation", ["Add Ride", "View Rides", "Ask for a Ride", "Messages"])

# Add Ride Page
if menu == "Add Ride":
    st.header("Add a New Ride")
    with st.form("new_ride_form"):
        time = st.time_input("Time")
        start_destination = st.text_input("Start Destination")
        end_destination = st.text_input("End Destination")
        fare = st.number_input("Fare", min_value=0)
        seats = st.number_input("Available Seats", min_value=1)
        contact_number = st.text_input("Contact Number")
        submit_button = st.form_submit_button(label="Add Ride")

    if submit_button:
        add_ride(time.strftime('%H:%M'), start_destination, end_destination, fare, seats, contact_number)
        st.success("Ride added successfully!")

# View Rides Page
elif menu == "View Rides":
    st.header("Available Rides")
    rides_df = get_rides()
    st.write(rides_df)

# Ask for a Ride Page
elif menu == "Ask for a Ride":
    st.header("Ask for a Ride")
    st.write("You can ask for a ride by filling out the form below.")
    with st.form("ask_for_ride_form"):
        time = st.time_input("Preferred Departure Time")
        start_destination = st.text_input("Starting Point")
        end_destination = st.text_input("Destination")
        contact_number = st.text_input("Your Contact Number")
        submit_button = st.form_submit_button(label="Ask for a Ride")

    if submit_button:
        add_passenger_request(time.strftime('%H:%M'), start_destination, end_destination, contact_number)
        st.success("Your request for a ride has been submitted. Drivers will contact you if they can provide a ride.")

# Messages Page
elif menu == "Messages":
    st.header("Messages")
    st.write("Here you can communicate with drivers who have provided rides.")

    # Select sender and receiver
    selected_sender = st.selectbox("Select Sender", ["Passenger", "Driver"])
    selected_receiver = st.selectbox("Select Receiver", ["Passenger", "Driver"])

    # Fetch messages based on sender and receiver
    messages_df = pd.DataFrame(columns=["Sender", "Receiver", "Message"])
    if selected_sender != selected_receiver:
        if selected_sender == "Passenger":
            sender = "Passenger"
            receiver = "Driver"
        else:
            sender = "Driver"
            receiver = "Passenger"

        messages_df = get_messages(sender, receiver)
        st.dataframe(messages_df)

    # Form to send message
    st.subheader("Send Message")
    with st.form("send_message_form"):
        message = st.text_input("Type your message")
        send_button = st.form_submit_button("Send")

    # Handle message submission
    if send_button:
        add_message(selected_sender, selected_receiver, message)
        st.success("Message sent successfully!")
