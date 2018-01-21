import os
import plaid
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from models import User

# Plaid API keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)

# access_token = None # does not expire, and it should be securely stored
# public_token = None # one-time use and expires after 30 minutes


@app.route('/')
@login_required
def index():
    accounts = []
    if current_user.access_token is not None:
        response = client.Accounts.get(current_user.access_token)
        accounts = response['accounts']
    return render_template('index.html', title='Home', plaid_public_key=PLAID_PUBLIC_KEY, plaid_environment=PLAID_ENV, accounts=accounts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/notifications')
def notifications():
    return render_template('notifications.html', title='Notifications')


@app.route('/get_access_token', methods=['POST'])
def get_access_token():
    public_token = request.form['public_token']
    exchange_response = client.Item.public_token.exchange(public_token)
    # print('public token: ' + public_token)
    print('access token: ' + exchange_response['access_token'])
    print('item ID: ' + exchange_response['item_id'])

    current_user.access_token = exchange_response['access_token']
    db.session.commit()

    # print(client.Auth.get(access_token)['accounts'])

    # # create a public_token for use with Plaid Link's update mode
    # create_response = client.Item.public_token.create(access_token)
    # # use the generated public_token to initialize Plaid Link in update
    # # mode for a user's Item so that they can provide updated credentials
    # # or MFA information
    # public_token = response['public_token']

    return jsonify(exchange_response)


@app.route('/clear_token')
def clear_token():
    client.Item.remove(current_user.access_token)
    current_user.access_token = None
    db.session.commit()
