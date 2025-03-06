import boto3
from config import BUCKET_NAME


class S3:
    # В домашней дирректории должна лежать папка ~/.aws/ с файлами credentials и config
    session = boto3.session.Session()
    s3 = session.client(service_name='s3')

    @classmethod
    def upload_object(cls, object, name: str):
        cls.s3.put_object(Bucket=BUCKET_NAME, Key=name, Body=object)

    @classmethod
    def get_object(cls, name: str):
        return cls.s3.get_object(Bucket=BUCKET_NAME, Key=name)["Body"].read()
