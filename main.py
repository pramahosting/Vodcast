# app/ui/main.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from app.auth import auth_manager
from app.video_generation.generate_video import generate_video_with_tts

from app.auth import auth_manager

# Ensure the DB and table is ready
auth_manager.create_user_table()
auth_manager.migrate_user_table()

st.set_page_config(page_title="Prama Vodcast", layout="wide")

default_email = st.session_state.get("saved_email", "")
default_password = st.session_state.get("saved_password", "")

# ---------- Session State Defaults ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "remember_me" not in st.session_state:
    st.session_state.remember_me = False
if "remembered_email" not in st.session_state:
    st.session_state.remembered_email = ""
if "remembered_password" not in st.session_state:
    st.session_state.remembered_password = ""

# ---------- Login ----------
def login_tab():
    st.subheader("🔐 Login to Prama Vodcast")

    # Rerun trigger initialization
    if "rerun_trigger" not in st.session_state:
        st.session_state.rerun_trigger = False

    email = st.text_input(
        "📧 Email",
        value=st.session_state.get("saved_email", ""),
        key="login_email"
    )
    password = st.text_input(
        "🔑 Password",
        value=st.session_state.get("saved_password", ""),
        type="password",
        key="login_password"
    )
    remember_me = st.checkbox("🔒 Remember me", key="remember_me")

    # Layout: Login button and Forgot Password button aligned in one line
    col_login, col_forgot = st.columns([1, 1])

    with col_login:
        if st.button("Login"):
            if not email or not password:
                st.warning("⚠️ Please enter email and password.")
            else:
                success, user_data_or_msg = auth_manager.authenticate_user(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_data = user_data_or_msg
                    st.session_state.email = user_data_or_msg["email"]
                    st.session_state.name = user_data_or_msg["name"]
                    st.session_state.is_admin = user_data_or_msg["is_admin"]

                    if remember_me:
                        st.session_state.saved_email = email
                        st.session_state.saved_password = password
                    else:
                        st.session_state.saved_email = ""
                        st.session_state.saved_password = ""

                    st.success(f"🎉 Welcome back, {st.session_state.name}!")
                    # Force rerun by toggling the flag
                    st.session_state.rerun_trigger = not st.session_state.rerun_trigger
                else:
                    st.error(user_data_or_msg)

        # Display success message below Login button if password reset succeeded
        if st.session_state.get("password_reset_success", False):
            st.success("✅ Password reset successfully! You can now log in with the new password.")

    with col_forgot:
        st.write("")  # Simple vertical alignment helper
        if not st.session_state.get("forgot_password", False):
            if st.button("Forgot Password?"):
                if not email:
                    st.warning("⚠️ Please enter your email above to reset your password.")
                else:
                    st.session_state.forgot_password = True
                    st.session_state.password_reset_success = False

    # Ensure flags exist
    if "forgot_password" not in st.session_state:
        st.session_state.forgot_password = False
    if "password_reset_success" not in st.session_state:
        st.session_state.password_reset_success = False

    # Forgot Password Flow
    if st.session_state.forgot_password and not st.session_state.password_reset_success:
        st.info(f"Reset password for {email}")
        new_password = st.text_input(
            "Enter New Password",
            type="password",
            key="new_password"
        )
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="confirm_new_password"
        )
        if st.button("Reset Password", key="reset_pw_btn"):
            if new_password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif not new_password:
                st.error("⚠️ Enter a valid password.")
            else:
                auth_manager.reset_password(email, new_password)
                st.session_state.password_reset_success = True
                st.session_state.forgot_password = False
                # Trigger rerun without any experimental methods
                st.session_state.rerun_trigger = not st.session_state.rerun_trigger

# ---------- Signup ----------
def signup_tab():
    st.subheader("Create an Account")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

    with col2:
        company_name = st.text_input("Company Name")
        contact_number = st.text_input("Contact Number")
        country = st.text_input("Country")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        elif not name or not email or not password:
            st.error("Please fill in all required fields.")
        else:
            created = auth_manager.signup_user(
                email=email,
                name=name,
                password=password,
                company_name=company_name,
                contact_number=contact_number,
                country=country
            )
            if created:
                st.success("✅ Account created successfully! You can now log in.")
            else:
                st.error("❌ Email already exists or signup failed.")

# ---------- Main App ----------
def show_main_app():
    st.sidebar.title("Agent Components")

    st.markdown("""
        <style>
        .main-header {
            font-size: 2.8em;
            font-weight: bold;
            margin-bottom: 0;
            color: #2c3e50;
            margin-top: -60px;  /* Push heading upward */
            text-align: center;
        }
        .sub-header {
            font-size: 0.8em !important;   /* increase a bit, but !important forces it */
            margin-top: 0px !important;
            margin-bottom: 10px !important;
            color: #555 !important;
            text-align: center !important;
        }
        .welcome-logout-container {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 10px;
            margin-top: -20px;
            margin-bottom: 10px;
        }
        .welcome-text {
            color: #27ae60; /* Green */
            font-weight: bold;
            font-size: 1.1em;
        }
        button.stButton {
            background-color: #ffe6e6 !important;
            color: #d9534f !important;
            border: 1px solid #d9534f !important;
            border-radius: 6px !important;
            padding: 6px 12px !important;
            font-weight: bold !important;
            margin: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    user_name = st.session_state.user_data.get("name", "User")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("<h1 style='text-align: center;'>🎙️ Prama Vodcast</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>AI Powered Vodcast Generator Agent</h4>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <style>
            .header-container {{
                display: flex;
                justify-content: flex-end;
                align-items: center;
                margin-top: 10px;
            }}
            .welcome-text {{
                margin-right: 12px;
                color: green;
                font-weight: bold;
                font-size: 1.1em;
            }}
            .logout-button {{
                background-color: #ffe6e6;
                color: #d9534f;
                border: 1px solid #d9534f;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
            }}

        </style>
    <div class="topbar">
        <div class="welcome-text">Welcome, {user_name}!</div>
    </div>
        """, unsafe_allow_html=True)

        # Detect logout submission
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state["logged_in"] = False
            st.experimental.rerun()

    # Sidebar logic
    choice = st.sidebar.radio(
        "Choose action",
        [
            "📤 Upload Speaker Video",
            "📝 Enter Script or Topic",
            "🎬 Generate Podcast",
            "📺 YouTube Publishing"
        ]
    )

    if choice == "📤 Upload Speaker Video":
        st.subheader("📹 Upload Speaker Video")
        uploaded_video = st.file_uploader("Upload an MP4 video of the speaker", type=["mp4"])
        if uploaded_video:
            st.session_state.uploaded_video = uploaded_video
            st.video(uploaded_video)
            st.success("✅ Video uploaded.")

    elif choice == "📝 Enter Script or Topic":
        st.subheader("✏️ Enter Podcast Script or Topic")
        topic_or_text = st.text_area("Write your podcast script or just enter a topic:", value=st.session_state.get("script_text", ""))
        st.session_state.script_text = topic_or_text
        auto_generate = st.checkbox("🤖 Use AI to generate script from topic", value=True)
        if st.button("Generate Script"):
            if topic_or_text:
                if auto_generate:
                    st.info("⚙️ AI script generation coming soon.")
                else:
                    st.success("✅ Script ready.")
            else:
                st.warning("⚠️ Please enter something.")

    elif choice == "🎬 Generate Podcast":
        st.subheader("🎥 Generate AI Vodcast")

        # Validate input
        if 'uploaded_video' not in st.session_state or not st.session_state.uploaded_video:
            st.warning("⚠️ Please upload a speaker video first under 'Upload Speaker Video'.")
        elif not st.session_state.get("script_text", ""):
            st.warning("⚠️ Please enter or generate a script first under 'Enter Script or Topic'.")
        else:
            if st.button("Generate Video"):
                with st.spinner("Generating video..."):
                    # Save uploaded video temporarily and extract features beforehand
                    uploaded_video = st.session_state.uploaded_video
                    script_text = st.session_state.script_text

                    # Save uploaded video to temp file
                    temp_video_path = f"temp_uploaded_video.mp4"
                    with open(temp_video_path, "wb") as f:
                        f.write(uploaded_video.getbuffer())

                    # Extract features (implement your extraction logic or placeholder)
                    feature_file_path = "data/features_extracted.pkl"
                    # For demo, assume features are extracted and saved here
                    # e.g., extract_features(temp_video_path, feature_file_path)

                    video_path = generate_video_with_tts(feature_file_path, script_text, "app/generated")

                    st.success("✅ Video generated!")
                    st.video(video_path)

                    # Provide download button
                    with open(video_path, "rb") as vid_file:
                        st.download_button(
                            label="⬇️ Download Video",
                            data=vid_file,
                            file_name="generated_podcast_video.mp4",
                            mime="video/mp4"
                        )

    elif choice == "📺 YouTube Publishing":
        st.subheader("📤 Publish to YouTube")
        st.info("⚙️ YouTube API integration coming soon.")

# ---------- Router ----------
if __name__ == "__main__":
    if st.session_state.authenticated:
        show_main_app()
    else:
        st.sidebar.title("🔑 Authentication")
        tab = st.sidebar.radio("Go to", ["Login", "Signup"])
        if tab == "Login":
            login_tab()
        else:
            signup_tab()
else:
    if st.session_state.authenticated:
        show_main_app()
    else:
        st.sidebar.title("🔑 Authentication")
        tab = st.sidebar.radio("Go to", ["Login", "Signup"])
        if tab == "Login":
            login_tab()
        else:
            signup_tab()
