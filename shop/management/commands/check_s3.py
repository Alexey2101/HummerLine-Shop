from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import time


class Command(BaseCommand):
    help = 'Check S3 (or S3-compatible) bucket connectivity and basic write/delete permissions.'

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_S3', False):
            self.stdout.write(self.style.WARNING('USE_S3 is not enabled in settings. Nothing to check.'))
            return

        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        if not bucket:
            self.stdout.write(self.style.ERROR('AWS_STORAGE_BUCKET_NAME is not set.'))
            sys.exit(2)

        session = boto3.session.Session(
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', None),
        )

        s3 = session.client('s3', endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None))

        self.stdout.write(f'Checking access to bucket: {bucket}')

        # 1) Try head_bucket (fast check)
        try:
            s3.head_bucket(Bucket=bucket)
            self.stdout.write(self.style.SUCCESS('Bucket exists and is reachable (head_bucket OK).'))
        except NoCredentialsError:
            self.stdout.write(self.style.ERROR('No AWS credentials found.'))
            sys.exit(3)
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'Bucket access error: {e}'))
            sys.exit(4)

        # 2) Try upload small test object and delete it
        key = f'healthcheck/check-{int(time.time())}.txt'
        try:
            s3.put_object(Bucket=bucket, Key=key, Body=b'OK', ACL='private')
            self.stdout.write(self.style.SUCCESS(f'Uploaded test object: {key}'))
        except ClientError as e:
            self.stdout.write(self.style.ERROR(f'Failed to upload test object: {e}'))
            sys.exit(5)

        try:
            s3.delete_object(Bucket=bucket, Key=key)
            self.stdout.write(self.style.SUCCESS('Deleted test object successfully.'))
        except ClientError as e:
            self.stdout.write(self.style.WARNING(f'Uploaded but failed to delete test object: {e}'))
            sys.exit(6)

        self.stdout.write(self.style.SUCCESS('S3 health-check completed successfully.'))