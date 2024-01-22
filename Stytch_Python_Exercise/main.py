import os
import sys

import dotenv
import stytch
from flask import Flask, render_template, request, redirect, url_for, session
import requests

from stytch import Client

# load the .env file
dotenv.load_dotenv()

# By default, run on localhost:4567
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "4567"))
MAGIC_LINK_URL = f"http://{HOST}:{PORT}/authenticate"

# Load the Stytch credentials, but quit if they aren't defined
STYTCH_PROJECT_ID = os.getenv("STYTCH_PROJECT_ID")
STYTCH_SECRET = os.getenv("STYTCH_SECRET")
if STYTCH_PROJECT_ID is None:
    sys.exit("STYTCH_PROJECT_ID env variable must be set before running")
if STYTCH_SECRET is None:
    sys.exit("STYTCH_SECRET env variable must be set before running")

stytch_client = stytch.Client(
    project_id=STYTCH_PROJECT_ID,
    secret=STYTCH_SECRET,
    environment="test",
)


# create a Flask web app
app = Flask(__name__)

app.secret_key = 's3cr3t_k3y_!@#$_2342_AaBbCc123'


@app.route("/")
def index() -> str:
    return render_template("loginOrSignUp.html")


@app.route("/login_or_create_user", methods=["POST"])
def login_or_create_user() -> str:
    if request.method == "POST":
        user_input = request.form.get("user_input")

        # Determine if the input is an email or phone number
        if "@" in user_input:
            # Handle email login or creation
            resp = stytch_client.magic_links.email.login_or_create(
                email=user_input,
                login_magic_link_url=MAGIC_LINK_URL,
                signup_magic_link_url=MAGIC_LINK_URL,
            )

            if resp.status_code != 200:
                print(resp)
                return "Something went wrong sending magic link"

            return render_template("emailSent.html")

        else:
            # Handle SMS login or creation
            # Ensure phone number is in E.164 format
            if not user_input.startswith("+"):
                user_input = f"+{user_input}"

            try:
                resp = stytch_client.otps.sms.login_or_create(
                    phone_number=user_input)

                if resp.status_code != 200:
                    return f"Error: {resp.error_message}"

                return render_template("smsSent.html")

            except Exception as e:
                return f"An error occurred: {e}"

    return render_template("loginOrSignUp.html")


@app.route("/authenticate")
def authenticate() -> str:
    # SMS OTP Authentication
    if "otp_code" in request.args:
        otp_code = request.args.get("otp_code")
        # For simplicity, I'm just using this phone_id because only I will be using this demo
        phone_id = 'phone-number-test-778e9eb1-bb49-40f6-a196-44b339a95013'

        if not phone_id:
            return "Phone ID not found in session", 400

        try:
            resp = stytch_client.otps.authenticate(
                method_id=phone_id, code=otp_code)
            print(resp.status_code)
            if resp.status_code == 200:
                session['user_authenticated'] = True
                # Redirect to a dashboard or home page
                return render_template("login.html")
            else:
                return "Invalid OTP", 400
        except Exception as e:
            return f"An error occurred: {e}", 500

    # Check if the token is from OAuth or Magic Link
    token_type = request.args.get("stytch_token_type")
    token = request.args.get("token")

    if token_type == "oauth":
        # Handle OAuth token
        resp = stytch_client.oauth.authenticate(token)
        if resp.status_code != 200:
            print(resp)
            return "Something went wrong with OAuth authentication"
        else:
            # session_token = resp.json().get('session_token')
            session['stytch_session_token'] = token
    elif token_type == "magic_links":
        # Handle Magic Link token
        resp = stytch_client.magic_links.authenticate(token)
        if resp.status_code != 200:
            print(resp)
            return "Something went wrong authenticating Magic Link token"
        else:
            # session_token = resp.json().get('session_token')
            session['stytch_session_token'] = token

    return render_template("login.html")


# handles the logout endpoint
@app.route("/logout")
def logout() -> str:
    # session_token = session.get('stytch_session_token')
    # print(session_token)
    # resp = stytch_client.sessions.revoke(session_token)
    return render_template("logout.html")


@app.route('/oauth/callback')
def oauth_callback():
    # Get the token from the query parameters
    token = request.args.get('token')

    # Authenticate the user with Stytch
    resp = stytch_client.oauth.authenticate(token)

    # Handle the response (e.g., create a session, redirect to profile)
    # ...

    return render_template("login.html")


# run's the app on the provided host & port
if __name__ == "__main__":
    # in production you would want to make sure to disable debugging
    app.run(host=HOST, port=PORT, debug=True)
