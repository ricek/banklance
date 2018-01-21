# Banklance

PennApps XVII project - Manage all your bank account alerts from one dashboard. [(Devpost)](https://devpost.com/software/banklance)

    git clone git@github.com:ricek/banklance.git
    python3 -m venv venv
    venv\Scripts\activate # on windows cmd
    pip install -r requirements.txt

Include following environment varibale in `venv\Scripts\actiavte.bat` file

    set "FLASK_APP=banklance.py"

    set "SECRET_KEY=somethingveryhardtoguess"
    set "DATABASE_URL=sqlite:///path_to_this_repo\banklance\app.db"

    set "PLAID_CLIENT_ID=get_from_plaid_dashboard"
    set "PLAID_SECRET=get_from_plaid_dashboard"
    set "PLAID_PUBLIC_KEY=get_from_plaid_dashboard"

Reactiavte the virtual environment and run `flask shell` to manually add test user account and lastly `flask run`

    from banklance import db
    from models import User
    u = User(username='test')
    u.set_password('blahblahblah')
    db.session.add(u)
    db.session.commit()
