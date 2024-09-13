import streamlit as st
from PIL import Image
from project import AICoverLetterGenerator
from connection import Database
import re

# Function to set up the app bar with custom CSS
def set_app_bar():
    st.markdown("""
        <style>
        .app-bar {
            background-color: #000000;
            padding: 0px 0px;
            text-align: center;
            border-bottom: 2px solid #FFA500;
            position: fixed;
            width: 100%;
            top: 0;
            left: 0;
            z-index: 1000;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.2);
        }
        .app-bar h2 {
            color: white;
            margin: 0;
            font-size: 24px;
        }
        body {
            margin: 0;
            padding-top: 80px;  /* Adjust padding to prevent content overlap */
        }
        /* Hide sidebar */
        .css-1l02t74, .css-1d391kg {
            display: none;
        }
        </style>
        <div class="app-bar">
            <h2>Dot Labs AI</h2>
        </div>
        """, unsafe_allow_html=True)

# Function to render the welcome screen
def render_welcome_screen():
    st.markdown("""
        <style>
        .welcome-screen {
            text-align: center;
            margin-top: 20px;
            font-size: 28px;
            color: #282c34;
            animation: fadeIn 1.5s ease-in-out;
        }
        .welcome-screen h1 {
            font-size: 48px;
            color: #FFA500;
            margin-bottom: 20px;
            margin-left: 20px;
            font-weight: bold;
        }
        .welcome-screen p {
            font-size: 18px;
            color: #6c757d;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }
        .stButton>button {
            width: 150px;
            height: 50px;
            font-size: 18px;
        }
        </style>
        <div class="welcome-screen">
            <h1>Welcome to Dot Labs AI!</h1>
        </div>
            """, unsafe_allow_html=True)
    
    # Load the image
    c1, c2, c3 = st.columns(3)
    with c2:
        img = Image.open("Dotlabs Logo white.png")
        st.image(img)

    st.markdown("""
        <style>
        .paragraph {
            text-align: center;
            animation: fadeIn 1.5s ease-in-out;
        }
        .paragraph p {
            font-size: 18px;
            color: #6c757d;
            margin-bottom: 40px;
        }
        </style>
        <div class="paragraph">
            <p>If you already have an account, click Login.</p>
            <p>Don't have an account? Click Sign Up to create one.</p>
        </div>
        <div class="button-container">
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("Login", key="welcome_login"):
            st.session_state["page"] = "login"
            st.rerun(scope="app")  # Trigger a rerun to apply the page transition
        if st.button("Signup", key="welcome_signup"):
            st.session_state["page"] = "signup"
            st.rerun(scope="app")  # Trigger a rerun to apply the page transition

    st.markdown("</div>", unsafe_allow_html=True)
global db
db = Database()
def handle_login():
    st.markdown("<h2>Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", key="login_password", type="password")
    
    if st.button("Login", key="login_button"):
        if db.check_user(username, password):
            db.set_username(username)
            print(username)
            
            st.session_state["logged_in"] = True
            st.session_state["page"] = "project"
            st.success("Logged in successfully!")
            st.experimental_set_query_params(page="project")
            st.rerun(scope="app")  # Trigger a rerun to update the page
        else:
            st.error("Invalid username or password")
    
    if st.button("Back to Welcome Screen", key="back_to_welcome_from_login"):
        st.session_state["page"] = "welcome"
        st.rerun(scope="app")  # Trigger a rerun to update the page

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Function to handle signup
def handle_signup():
    st.markdown("<h2>Signup</h2>", unsafe_allow_html=True)
    first_name = st.text_input("First Name", key="f_name")
    last_name = st.text_input("Last Name", key="l_name")
    username = st.text_input("Username", key="signup_username")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", key="signup_password", type="password")
    confirm_password = st.text_input("Confirm Password", key="signup_confirm_password", type="password")

    if st.button("Signup", key="signup_button"):
        if not is_valid_email(email):
            st.error("Invalid email address.")
        elif password == confirm_password:
            db.insert_user(first_name, last_name, username, password, email, confirm_password)
            db.set_username(username)
            st.session_state["logged_in"] = True
            st.session_state["page"] = "welcome"
            st.success("Signed up successfully!")
            st.rerun(scope="app")  # Trigger a rerun to update the page
        else:
            st.error("Passwords do not match.")
    
    if st.button("Back to Welcome Screen", key="back_to_welcome_from_signup"):
        st.session_state["page"] = "welcome"
        st.rerun(scope="app")


def handle_admin_login():
    st.markdown("<h2>Admin Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username", key="admin_login_username")
    password = st.text_input("Password", key="admin_login_password", type="password")

    if st.button("Login", key="admin_login_button"):
        if username == "nouman" and db.check_admin(username, password):
            st.session_state["admin_logged_in"] = True
            st.session_state["page"] = "admin_dashboard"
            st.success("Logged in successfully!")
            st.experimental_set_query_params(page="admin_dashboard")
            st.rerun(scope="app")  # Trigger a rerun to update the page
        else:
            st.error("Invalid username or password")

    if st.button("Back to Welcome Screen", key="admin_back_to_welcome_from_login"):
        st.session_state["page"] = "welcome"
        st.rerun(scope="app")  # Trigger a rerun to update the page

# Function to render pages based on session state
st.set_page_config(page_title="AI Chatbot with Upwork Job Proposal Generator", layout="centered")
def render_page():
    page = st.session_state.get("page", "welcome")
    set_app_bar()
    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"
    if page == "project":
        api_key = "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"
        db_config = {
            'db_host': 'localhost',
            'db_name': 'project',
            'db_user': 'postgres',
            'db_password': 'admin',
            'db_port': 5432
        }
        app = AICoverLetterGenerator(api_key, db_config=db_config)
        app.run_app() 
    elif page == "welcome":
        render_welcome_screen()
    elif page == "login":
        handle_login()
    elif page == "signup":
        handle_signup()

# Main function to run the app
if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state['page'] = 'welcome'
    render_page()
