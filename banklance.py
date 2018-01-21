import os
import plaid
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SECRET_KEY = os.getenv('SECRET_KEY')

# Plaid API keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)

access_token = None # does not expire, and it should be securely stored
public_token = None # one-time use and expires after 30 minutes


@app.route('/')
def index():
    accounts = []
    if access_token is not None:
        response = client.Accounts.get(access_token)
        accounts = response['accounts']
    return render_template('index.html', title='Home', plaid_public_key=PLAID_PUBLIC_KEY, plaid_environment=PLAID_ENV, accounts=accounts)


@app.route('/login')
def login():
    return render_template('login.html', title='Sign In')


@app.route("/get_access_token", methods=['POST'])
def get_access_token():
    global access_token
    public_token = request.form['public_token']
    exchange_response = client.Item.public_token.exchange(public_token)
    # print('public token: ' + public_token)
    print('access token: ' + exchange_response['access_token'])
    print('item ID: ' + exchange_response['item_id'])

    access_token = exchange_response['access_token']

    # print(client.Auth.get(access_token)['accounts'])

    # # create a public_token for use with Plaid Link's update mode
    # create_response = client.Item.public_token.create(access_token)
    # # use the generated public_token to initialize Plaid Link in update
    # # mode for a user's Item so that they can provide updated credentials
    # # or MFA information
    # public_token = response['public_token']

    return jsonify(exchange_response)
