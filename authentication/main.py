import base64
import datetime
import hashlib
import smtplib
import boto3
import pyrebase
from getpass import getpass
import pyotp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": ""

}


def log_in():
    global user, email, password, phone
    try:
        phone = database.child("users").child(hashlib.sha256(
            email.encode()).hexdigest()).child().get().val()['Phone']
    except:
        print("Phone record not found.")
        get_phone()
    try:
        user = auth.sign_in_with_email_and_password(email, password)
    except Exception as e:
        print("Invalid Credentials. Please check and try again.")
        print("Email: " + email)
        x = input("Reset password (y/n) : ")
        if x == "y":
            auth.send_password_reset_email(email)
        email = input("Enter email : ")
        password = getpass()
        log_in()


def otp_sender():
    totp = pyotp.TOTP(base64.b32encode(
        (email + datetime.datetime.now().strftime("%H%M%S")).encode()), interval=300)
    message = "The otp for login is : " + totp.now() + " is valid for 5 minutes."
    sender_email = "email@example.com"
    sender_password = "password"

    msg = MIMEMultipart('alternative')

    msg['Subject'] = "OTP FOR 2 Factor Authentication"
    msg['From'] = sender_email
    msg['To'] = email
    part1 = MIMEText(message, 'text/plain')
    sender_title = "Anish Bhattacharya"
    recipient = email
    msg.attach(part1)
    server = smtplib.SMTP_SSL('smtp.zoho.eu', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, [recipient], msg.as_string())
    server.quit()
    print("OTP is sent successfully to %s" % recipient)
    otp_verify(totp)


def otp_verify(totp):
    code = input("Enter OTP : ")
    if totp.verify(code):
        print("OTP verified successfully")
    else:
        print("OTP verification failed")
        print("New OTP generated, and is sent to your email!")
        otp_sender()
        otp_verify()


def get_phone():
    global phone, user, email
    phone = input(
        "Please enter your phone number (with country code) [+91907xxxxxxx]: ")
    database.child("users").child(hashlib.sha256(
        email.encode()).hexdigest()).update({"Phone": phone})


def send_phone_verification():
    global phone
    totp = pyotp.TOTP(base64.b32encode(
        (phone + datetime.datetime.now().strftime("%H%M%S")).encode()), interval=300)

    sns = boto3.client('sns',
                       aws_access_key_id="",
                       aws_secret_access_key="",
                       region_name="ap-southeast-1")

    response = sns.publish(
        PhoneNumber=phone,
        Message="The otp for login is : " + totp.now() + " is valid for 5 minutes."
    )

    verify_phone(totp)


def verify_phone(totp):
    code = input("Enter OTP sent on your phone : ")
    if totp.verify(code):
        print("OTP verified successfully")
    else:
        print("OTP verification failed")
        print("New OTP generated, and is sent to your phone!")
        send_phone_verification()


if __name__ == '__main__':
    firebase = pyrebase.initialize_app(config)
    auth = firebase.auth()
    database = firebase.database()
    x = input("1. Log In (Default)\n2. Sign Up\n Input : ")
    if x == "2":
        x = 2
    else:
        x = 1
    email = input("Enter email : ")
    password = getpass()
    if x == 2:
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user['idToken'])
            print("Email Verification Link has been sent to your email")
            get_phone()
        except:
            print("Email may exist! Redirecting to Login page now!")
            log_in()
    if x == 1:
        log_in()

    verified = auth.get_account_info(user['idToken'])
    verified = (verified['users'][0]['emailVerified'])
    while not verified:
        print("Please verify your email to continue further")
        x = input("Press any key to continue.")
        verified = auth.get_account_info(user['idToken'])
        verified = (verified['users'][0]['emailVerified'])

    otp_sender()

    username = auth.get_account_info(user['idToken'])
    username = username['users'][0]['email']
    print("You are signed in as " + username)
    send_phone_verification()
