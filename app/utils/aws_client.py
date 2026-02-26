import os
import boto3

def get_dynamodb_resource():
    """
    Initializes and returns the DynamoDB resource.
    In production, AWS credentials should be managed via IAM roles or environment variables.
    """
    return boto3.resource(
        'dynamodb',
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )