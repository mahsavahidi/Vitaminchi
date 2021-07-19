import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("__name__")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:vb12VB12@10.10.0.97:5432/postgres'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), unique=False)
    last_name = db.Column(db.String(255), unique=False)
    email = db.Column(db.String(255), unique=False)
    password = db.Column(db.String(255), unique=False)
    gender = db.Column(db.String(255), unique=False)
    mobile = db.Column(db.String(255), unique=False)
    company_name = db.Column(db.String(255), unique=False)
    token = db.Column(db.String(255), unique=False)
    confirmation_code = db.Column(db.String(255), unique=False)
    user_type = db.Column(db.String(255), unique=False)

    def __init__(self, first_name, last_name, email, password, gender, mobile, company_name, token, confirmation_code, user_type):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.gender = gender
        self.mobile = mobile
        self.company_name = company_name
        self.token = token
        self.confirmation_code = confirmation_code
        self.user_type = user_type


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    transaction_number = db.Column(db.String(255))
    status = db.Column(db.String(255))
    price = db.Column(db.String(255))
    plan_type = db.Column(db.String(255))
    token = db.Column(db.String(255))

    def __init__(self, date, transaction_number, status, price, plan_type, token):
        self.date = date
        self.transaction_number = transaction_number
        self.status = status
        self.price = price
        self.plan_type = plan_type
        self.token = token


if __name__ == '__main__':
    db.create_all()