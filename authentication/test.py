import base64
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

email = "anish_bhattacharya@gmail.com"
firebase = pyrebase.initialize_app(config)
database = firebase.database()
phone = database.child("users").child(
    hashlib.sha256(email.encode()).hexdigest()).child().get()
print(phone.val()['Phone'])


# phone = "+917980212255"
# database.child("users").child(hashlib.sha256(email.encode()).hexdigest()).update({"Phone": phone})
