import streamlit as st
from components.user_management import load_users, save_user
from components.ui_components import show_status_message


def render_signin_page(**kwargs):
    """Renders the modern sign-in/sign-up page."""
    
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🔐 Welcome to MovieMind</h1>
            <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8); margin-bottom: 2rem;">
                Sign in to unlock personalized movie recommendations
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create tabs for sign in and sign up
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
    
    with tab1:
        render_signin_tab()
    
    with tab2:
        render_signup_tab()
    
    # Back to home button
    st.markdown("---")
    if st.button("🏠 Back to Home", help="Return to the home page"):
        st.session_state.page = "home"
        st.rerun()


def render_signin_tab():
    """Render the sign-in tab."""
    st.markdown(
        """
        <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.3); 
                    border-radius: 15px; padding: 2rem; margin: 1rem 0;">
            <h3 style="color: #4ecdc4; text-align: center; margin-bottom: 2rem;">Welcome Back!</h3>
        """,
        unsafe_allow_html=True
    )
    
    with st.form("signin_form"):
        username = st.text_input(
            "👤 Username",
            placeholder="Enter your username",
            help="Enter the username you used when signing up"
        )
        
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password",
            help="Enter your password"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button(
                "🔑 Sign In",
                use_container_width=True,
                help="Sign in to your account"
            )
    
    if submit_button:
        if not username or not password:
            show_status_message("⚠️ Please enter both username and password.", "warning")
        else:
            users = load_users()
            user_found = False
            
            for user in users:
                if user.get("username") == username and user.get("password") == password:
                    st.session_state.current_user = user.get("id")
                    st.session_state.current_username = username
                    st.session_state.authenticated = True
                    
                    # Save authentication state to file
                    from components.auth_manager import save_auth_state
                    save_auth_state(username, user.get("id"))
                    
                    st.session_state.page = "home"
                    show_status_message(f"✅ Welcome back, {username}!", "success")
                    st.rerun()
                    user_found = True
                    break
            
            if not user_found:
                show_status_message("❌ Invalid username or password. Please try again.", "error")
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_signup_tab():
    """Render the sign-up tab."""
    st.markdown(
        """
        <div style="background: rgba(255, 152, 0, 0.1); border: 1px solid rgba(255, 152, 0, 0.3); 
                    border-radius: 15px; padding: 2rem; margin: 1rem 0;">
            <h3 style="color: #ff9800; text-align: center; margin-bottom: 2rem;">Join MovieMind!</h3>
        """,
        unsafe_allow_html=True
    )
    
    with st.form("signup_form"):
        new_username = st.text_input(
            "👤 Choose Username",
            placeholder="Enter a unique username",
            help="Choose a username that's not already taken"
        )
        
        new_password = st.text_input(
            "🔒 Choose Password",
            type="password",
            placeholder="Enter a secure password",
            help="Choose a strong password"
        )
        
        confirm_password = st.text_input(
            "🔒 Confirm Password",
            type="password",
            placeholder="Confirm your password",
            help="Re-enter your password to confirm"
        )
        
        email = st.text_input(
            "📧 Email (Optional)",
            placeholder="Enter your email address",
            help="Optional: Enter your email for account recovery"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button(
                "📝 Create Account",
                use_container_width=True,
                help="Create your MovieMind account"
            )
    
    if submit_button:
        # Validate input
        if not new_username or not new_password:
            show_status_message("⚠️ Please enter both username and password.", "warning")
        elif new_password != confirm_password:
            show_status_message("❌ Passwords do not match. Please try again.", "error")
        elif len(new_password) < 4:
            show_status_message("⚠️ Password must be at least 4 characters long.", "warning")
        else:
            # Check if username already exists
            users = load_users()
            username_exists = any(user.get("username") == new_username for user in users)
            
            if username_exists:
                show_status_message("❌ Username already exists. Please choose a different one.", "error")
            else:
                # Create new user
                new_user_id = len(users) + 1
                new_user = {
                    "id": new_user_id,
                    "username": new_username,
                    "password": new_password,
                    "email": email if email else "",
                    "created_at": "2024-01-01"  # You could add datetime import for current time
                }
                
                if save_user(new_user):
                    st.session_state.current_user = new_user_id
                    st.session_state.current_username = new_username
                    st.session_state.authenticated = True
                    
                    # Save authentication state to file
                    from components.auth_manager import save_auth_state
                    save_auth_state(new_username, new_user_id)
                    
                    st.session_state.page = "home"
                    show_status_message(f"✅ Account created successfully! Welcome, {new_username}!", "success")
                    st.rerun()
                else:
                    show_status_message("❌ Error creating account. Please try again.", "error")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show benefits of signing up
    st.markdown("---")
    st.markdown(
        """
        <h3 style="text-align: center; margin: 2rem 0;">🎁 Benefits of Signing Up</h3>
        """,
        unsafe_allow_html=True
    )
    
    benefits_col1, benefits_col2 = st.columns(2)
    
    with benefits_col1:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">🎬 Personal Watchlist</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    Save movies you want to watch later
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #ff6b6b; margin-bottom: 0.5rem;">⭐ Rate & Review</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    Rate movies and write reviews
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with benefits_col2:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">🤖 AI Recommendations</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    Get personalized movie suggestions
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <h4 style="color: #ff6b6b; margin-bottom: 0.5rem;">📚 Watch History</h4>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
                    Track your movie watching history
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
