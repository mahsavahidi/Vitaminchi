from models import User, db, app, Bill
import re
import uuid
from flask import jsonify, request
from passlib.hash import pbkdf2_sha256
from flask_mail import Mail, Message
import random
import datetime

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '****'
app.config['MAIL_PASSWORD'] = '****'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


@app.route('/api/v1/user/registration/', methods=['POST'])
def registration():
    # set fields for registration

    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    mobile_regex = '^09\d{9}$'
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    gender = request.json.get('gender')
    mobile = request.json.get('mobile')
    password = pbkdf2_sha256.hash(str(request.json.get('password')))
    email = request.json.get('email')
    company_name = request.json.get("company_name")
    user_type = request.json.get("user_type")
    exist_email = User.query.filter_by(email = email).all()
    print(exist_email)

    # check if user has company name
    if len(company_name) >= 1:
        company_name = company_name
    else:
        company_name = None

    # check if gender is correct

    if gender == 'f':
        gender = 'f'
    elif gender == 'm':
        gender = 'm'
    else:
        return 'gender is not valid'

    # check for user type
    if user_type == "haghighi":
        user_type = "haghighi"
    elif user_type == "hoghooghi":
        if company_name is None:
            return "company name should set"
        else:
            user_type = "hoghooghi"

    else:
        return "user type must set correctly"
    # check if email exists
    if len(exist_email) >= 1:
        return "email already exists"
    else:
        # check if type of email and mobile is correct
        if re.search(regex, email) and re.search(mobile_regex, mobile):
            p = User(first_name=first_name, last_name=last_name, email=email, password=password,
                     gender=gender, mobile=mobile, company_name=company_name, token=None, confirmation_code=None ,user_type=user_type)
            db.session.add(p)
            db.session.commit()
            send_verification_email(email)

            return email
        else:
            return "email or mobile is not valid"


# send verification email for user

def send_verification_email(email):
    msg = Message(
        'Email Confirmation',
        sender='vahidimahsa17@gmail.com',
        recipients=[email]
    )
    random_number = random.randint(1000, 9999)

    User.query.filter_by(email=email).update(dict(confirmation_code=random_number))
    db.session.commit()
    msg.body = 'your confirmation code is:' + '\n' + str(random_number)
    mail.send(msg)
    return "ok email"


# confirm email with code
@app.route('/api/v1/user/confirm-email/<email>', methods=['POST'])
def confirm_email(email):
    candidate_confirmation_code = request.json.get('confirmation_code')
    exist_email = User.query.filter_by(email=email).first()
    confirmation_code = exist_email.confirmation_code
    print(confirmation_code)
    if len(confirmation_code) >= 1:

        if confirmation_code == candidate_confirmation_code:
            token = uuid.uuid4().hex
            User.query.filter_by(email=email).update(dict(token=token, confirmation_code=None))
            db.session.commit()
            return jsonify(token=token)
        return jsonify(error="code is invalid")
    return jsonify(error="email is not available")


# login with email

@app.route('/api/v1/user/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        password_candidate = request.json.get('password')

        exist_email = User.query.filter_by(email=email).all()
        print(exist_email)
        if len(exist_email) >= 1:
            for x in exist_email:
                password = x.password
                token = x.token

                if pbkdf2_sha256.verify(password_candidate, password):
                    return jsonify(token=token)
                else:
                    return jsonify(error="password is not correct")
        else:
            return jsonify(error="email is not available")

    elif request.method == 'GET':
        email_z = request.args['email']

        return jsonify(token=email_z)


# reset password

@app.route('/api/v1/user/reset-password/', methods=['POST'])
def reset_password():
    candidate_token = request.headers.get('Authorization')
    email = request.json.get('email')
    current_password = request.json.get('current_password')
    new_password = request.json.get('new_password')
    exist_email = User.query.filter_by(email=email).all()
    if len(exist_email) >= 1:
        for x in exist_email:
            password = x.password
            token = x.token
            if candidate_token == token:
                if pbkdf2_sha256.verify(current_password, password):
                    token = uuid.uuid4().hex
                    User.query.filter_by(email=email).update(dict(token=token, password=pbkdf2_sha256.hash(str(new_password))))
                    db.session.commit()
                    return jsonify(token=token)
                return jsonify(error="Password doesn't match")
            return jsonify(error="Not Authorized")
    return jsonify(error="email is not correct")


# forget password and reset it using confirmation email

@app.route('/api/v1/user/forget-password/<email>', methods=['POST', 'GET'])
def forget_password(email):
    if request.method == 'GET':
        exist_email = User.query.filter_by(email=email).all()
        if len(exist_email) >= 1:
            send_verification_email(email)
            return jsonify(message="confirmation email sent!")
        else:
            return jsonify(error="email is not available")
    elif request.method == 'POST':
        confirmation_code = request.json.get("confirmation_code")
        password = pbkdf2_sha256.hash(str(request.json.get('password')))
        confirm_password = request.json.get('confirm_password')
        exist_email = User.query.filter_by(email=email).all()
        print(exist_email)
        if len(exist_email) >= 1:
            for x in exist_email:
                if confirmation_code == x.confirmation_code:
                    print(x.confirmation_code)
                    if pbkdf2_sha256.verify(confirm_password, password):
                        token = uuid.uuid4().hex
                        z = User.query.filter_by(email=email).update(dict(token=token, password=pbkdf2_sha256.hash(str(password)), confirmation_code=None))
                        print(z)
                        # db.session.commit()
                        return jsonify(token=token)
                    return jsonify(error="password doesn't match")
                return jsonify(error="confirmation code is not correct")
            return jsonify(error="email doesn't exist")


@app.route('/api/v1/panel', methods=['GET'])
def profile():
    days_left = ""
    plan_type = ""
    candidate_token = request.headers.get('Authorization')
    today = datetime.datetime.today()

    today_timestamp = datetime.datetime.timestamp(today)
    print(today, today_timestamp)
    exist_token = User.query.filter_by(token=candidate_token).all()
    if len(exist_token) >= 1:
        bill_token = Bill.query.filter_by(token=candidate_token).all()
        if len(bill_token) >= 1:
            for x in bill_token:
                date = x.date
                plan_type = x.plan_type
                days_left = date - today_timestamp

        return jsonify(error="token in wrong")
    for z in exist_token:
        return jsonify(
            message={
                "first_name" : z.first_name,
                "last_name" : z.last_name,
                "email": z.email,
                "mobile": z.mobile,
                "company_name": z.company_name,
                "user_type": z.user_type,
                "plan_type": plan_type,
                "days_left": days_left
            }
        )


if __name__ == '__main__':
    app.run()