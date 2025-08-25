import streamlit as st
from components.user_management import authenticate_user, save_user


def render_signin_page(**kwargs):
    """Renders the sign-in and sign-up page."""
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if not st.session_state.show_signup:
        st.subheader("Sign In")
        signin_email = st.text_input("Email", key="signin_email")
        signin_password = st.text_input("Password", type="password", key="signin_password")
        if st.button("Sign In", key="signin_btn"):
            if authenticate_user(signin_email, signin_password):
                st.session_state.current_user = signin_email
                st.session_state.current_username = signin_email
                st.session_state.page = "home"
                st.rerun()  # Use rerun to immediately navigate to the home page
            else:
                st.error("Invalid email or password.")
        st.markdown(
            "<div style='text-align:center; margin-top:18px;'>", unsafe_allow_html=True
        )
        if st.button("Not registered? Click here to Sign Up", key="show_signup_btn"):
            st.session_state.show_signup = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.title("Sign Up")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input(
            "Password", type="password", key="signup_password"
        )
        if st.button("Sign Up", key="signup_btn"):
            if save_user(signup_email, signup_password):
                st.success("Account created! Please sign in.")
                st.session_state.show_signup = False
                st.rerun()
            else:
                st.error("Email already registered.")
        if st.button("Back to Sign In", key="back_to_signin"):
            st.session_state.show_signup = False
            st.rerun()
