import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime, timezone

class DynamoDBService:
    def __init__(self):
        # Connect to the DynamoDB Local Docker container
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url='http://localhost:8000',
            region_name='us-east-1',
            aws_access_key_id='dummy',
            aws_secret_access_key='dummy'
        )
        self.table_name = 'TaskActivityLog'
        self.table = self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Creates the TaskActivityLog table if it doesn't exist."""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Assessment Requirement: user_id (Partition) and timestamp (Sort)
                return self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'timestamp', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                )
            raise e

    def log_activity(self, user_id, action, task_id, details=None, ip_address="127.0.0.1"):
        """Logs task mutations (created, updated, deleted) to DynamoDB."""
        if details is None:
            details = {}
            
        item = {
            'user_id': str(user_id),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'activity_id': str(uuid.uuid4()),
            'action': action,
            'task_id': str(task_id),
            'details': details,
            'ip_address': ip_address
        }
        self.table.put_item(Item=item)
        return item

# Create a singleton instance to use across the app
dynamo_service = DynamoDBService()