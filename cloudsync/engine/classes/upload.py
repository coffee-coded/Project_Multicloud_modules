import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import simplejson as json
from classes.bcolors import bcolors


class AwsUpload:
    def __init__(self):
        self.old_file = open("/mnt/d/anish/projects/project_multicloud/engine/classes/credentials.json", "r+")

        self.data = json.loads(self.old_file.read())
        key1 = self.data["Access key"]
        if key1 == "":
            self.data["Access key"] = input("Enter the Access key: ")
        else:
            self.ACCESS_KEY = key1
        key2 = self.data["Secret key"]
        if key2 == "":
            self.data["Secret key"] = input("Enter the Secret key: ")
        else:
            self.SECRET_KEY = self.data["Secret key"]
        key3 = self.data["Bucket Name"]
        if key3 == "":
            self.data["Bucket Name"] = input("Enter the Bucket Name: ")
        else:
            self.bucket = self.data["Bucket Name"]
        user = self.data["user"]
        if user == "":
            self.data["user"] = input("Enter the Bucket Name: ")
        else:
            self.user = self.data["user"]
            print(bcolors.WARNING+"Signed in as : ", user+bcolors.ENDC)

    def upload_to_aws(self, local_file):
        s3_file = local_file.split('/')[-1]

        s3 = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY,
                          aws_secret_access_key=self.SECRET_KEY)

        try:
            s3.upload_file(local_file, self.bucket, s3_file)
            print(bcolors.WARNING+"Upload Successful"+bcolors.ENDC)
            return True
        except FileNotFoundError:
            print(bcolors.FAIL+"The file was not found"+bcolors.ENDC)
            return False
        except NoCredentialsError:
            print(bcolors.BOLD+bcolors.HEADER+bcolors.OKBLUE+"Credentials not available"+bcolors.ENDC)
            return False

    def remove_from_aws(self, local_file):
        s3 = boto3.client('s3', aws_access_key_id=self.ACCESS_KEY,
                          aws_secret_access_key=self.SECRET_KEY)
        try:
            s3.delete_object(Bucket=self.bucket, Key=local_file)
        except ClientError as e:
            print("Error : ", e)
            return False
        return True
