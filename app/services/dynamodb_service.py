import boto3
from botocore.exceptions import EndpointConnectionError, ClientError
from boto3.dynamodb.conditions import Key
import uuid
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class DynamoDBService:
    def __init__(self):
        self.dynamodb = None
        self.table = None
        self._initialize_connection()

    def _initialize_connection(self):
        # FIX 5.1: Try-except wrapper to prevent app crash if DynamoDB Local is down
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:8000',
                region_name='us-east-1',
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy'
            )
            self._create_table_if_not_exists()
        except Exception as e:
            logger.warning(f"DynamoDB Local not running. Activity logging disabled. Error: {e}")
            self.dynamodb = None

    def _create_table_if_not_exists(self):
        try:
            # Check if table exists
            existing_tables = [table.name for table in self.dynamodb.tables.all()]
            if 'TaskActivityLogs' not in existing_tables:
                self.table = self.dynamodb.create_table(
                    TableName='TaskActivityLogs',
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
                self.table.meta.client.get_waiter('table_exists').wait(TableName='TaskActivityLogs')
            else:
                self.table = self.dynamodb.Table('TaskActivityLogs')
        except Exception as e:
            logger.error(f"Failed to verify/create DynamoDB table: {e}")
            self.dynamodb = None

    def log_activity(self, user_id, action, task_id, details, ip_address):
        if not self.dynamodb or not self.table:
            return # Graceful degradation if DB is down
            
        try:
            self.table.put_item(
                Item={
                    'user_id': str(user_id),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'activity_id': str(uuid.uuid4()),
                    'action': action,
                    'task_id': str(task_id),
                    'details': details,
                    'ip_address': ip_address
                }
            )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")

    # Added method to fetch activity logs
    def get_activities(self, user_id, action=None, task_id=None, date_from=None, date_to=None):
        if not self.dynamodb or not self.table:
            return []
        try:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(str(user_id)),
                ScanIndexForward=False
            )
            items = response.get('Items', [])
            
            # Apply Issue 6 Filters
            filtered_items = []
            for item in items:
                if action and item.get('action') != action: continue
                if task_id and item.get('task_id') != str(task_id): continue
                if date_from and item.get('timestamp') < date_from: continue
                if date_to and item.get('timestamp') > date_to: continue
                filtered_items.append(item)
                
            return filtered_items
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to fetch activities: {e}")
            return []

dynamo_service = DynamoDBService()