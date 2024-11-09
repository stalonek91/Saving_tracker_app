import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# Initialize Supabase client
# Replace with your actual Supabase URL and anon key
SUPABASE_URL = "https://ltjdczjnuqvctrdeatme.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0amRjempudXF2Y3RyZGVhdG1lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzExNTU3ODIsImV4cCI6MjA0NjczMTc4Mn0.Nj9AznmBSsm2NbxdN3Y1BtZX1ZbcyBJrDGvTxmTLNs8"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page config
st.set_page_config(
    page_title="Savings Tracker",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login(email, password):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.authenticated = True
        st.session_state.user = auth_response.user
        # Store the session
        st.session_state.session = auth_response.session
        return True
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

# Login form if not authenticated
if not st.session_state.authenticated:
    st.title("Login to Savings Tracker")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(email, password):
            st.rerun()
    
    # Add signup option
    if st.button("Sign Up"):
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            st.success("Signup successful! Please check your email and then login.")
        except Exception as e:
            st.error("Signup failed")
    
    st.stop()

def load_savings():
    """Load savings from Supabase"""
    try:
        supabase.auth.set_session(st.session_state.session.access_token, 
                                st.session_state.session.refresh_token)
        response = supabase.table('savings').select('*').execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error loading savings: {str(e)}")
        return []

def calculate_total(savings):
    """Calculate total from savings list"""
    return sum(float(item['amount']) for item in savings)

def add_saving(amount, description):
    """Add new saving to Supabase"""
    try:
        # Set the auth header with the current session
        supabase.auth.set_session(st.session_state.session.access_token, 
                                st.session_state.session.refresh_token)
        
        data = {
            'amount': amount,
            'description': description,
            'user_id': st.session_state.user.id
        }
        supabase.table('savings').insert(data).execute()
    except Exception as e:
        st.error(f"Error adding saving: {str(e)}")

def delete_saving(entry_id):
    """Delete saving from Supabase"""
    supabase.table('savings').delete().eq('id', entry_id).execute()

# App title
st.title("💰 Savings Tracker")

# Add logout button
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

# Load current savings
savings_data = load_savings()
total_savings = calculate_total(savings_data)

# Display total
st.header(f"Total Savings: PLN {total_savings:.2f}")

# Input fields
amount = st.number_input(
    "Enter amount to save:",
    min_value=0.0,
    step=1.0,
    format="%.2f"
)

description = st.text_input(
    "What did you save on?",
    placeholder="e.g., Groceries, Coffee, Transport"
)

if st.button("Add Savings"):
    if amount > 0:
        add_saving(amount, description)
        st.success(f"Added PLN {amount:.2f}")
        st.rerun()

# Show savings history with delete buttons
if savings_data:
    st.subheader("Savings History")
    
    # Create columns for each entry
    for entry in sorted(savings_data, key=lambda x: x['created_at'], reverse=True):
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
        with col1:
            st.write(f"#{entry['id']}")
        with col2:
            st.write(f"PLN {float(entry['amount']):.2f}")
        with col3:
            st.write(entry['description'])
        with col4:
            if st.button("🗑️", key=f"delete_{entry['id']}"):
                delete_saving(entry['id'])
                st.rerun()

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)