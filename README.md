# Stytch

Testing out Stytch's APIs to create a simple Python Flask web application

##### Prerequisites

Ensure you have pip, python and virtualenv installed

##### 1. Clone the repository.

Close this repository and navigate to the folder with the source code on your machine in a terminal window.

##### 2. Setup a virtualenv

We suggest creating a [virtualenv](https://docs.python.org/3/library/venv.html) and activating it to avoid installing dependencies globally

- `virtualenv -p python3 venv`
- `source venv/bin/activate`

##### 3. Install dependencies:

`pip install -r requirements.txt`

##### 4. Run the Server

Run `python3 main.py`
If you're interested in running async instead, run `python3 main_async.py`

##### 5. Login

Visit `http://localhost:3000` and login with your email.
Then check for the Stytch email and click the sign in button.
You should be signed in!

**NOTE:** When creating the SMS sign up/login, I just set it up with the assumption that I'm the only one using this demo app, so the phone_id/method_id is set to a value (linked to my user in the dashboard)
