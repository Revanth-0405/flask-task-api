import json
from unittest.mock import patch

# Use @patch to intercept the DynamoDB call in your TaskService
@patch('app.services.task_service.dynamo_service.log_activity')
def test_create_task_success(mock_log_activity, client, auth_headers):
    # 1. Prepare the test data
    payload = {
        "title": "Finish Phase 4 Testing",
        "description": "Write pytest functions for the Flask API",
        "priority": "high"
    }

    # 2. Make the POST request
    response = client.post(
        '/api/tasks/',
        data=json.dumps(payload),
        content_type='application/json',
        headers=auth_headers
    )

    if response.status_code != 201:
        print("\n Hidden API Error", response.get_json())

    # 3. Assert the expected outcomes
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Finish Phase 4 Testing"
    assert data["priority"] == "high"
    
    # 4. (Optional but cool) Verify that our code ATTEMPTED to call DynamoDB
    mock_log_activity.assert_called_once()

def test_get_tasks_unauthorized(client):
    response = client.get('/api/tasks/')
    assert response.status_code == 401