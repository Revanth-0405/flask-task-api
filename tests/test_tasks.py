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

# tests/test_tasks.py (Append these to the bottom of the file)

def test_get_all_tasks(client, auth_headers):
    # 1. Fetch the list of tasks
    response = client.get('/api/tasks/', headers=auth_headers)
    
    # 2. Assert it succeeds and returns the expected pagination structure
    assert response.status_code == 200
    data = response.get_json()
    assert "tasks" in data
    assert "meta" in data

@patch('app.services.task_service.dynamo_service.log_activity')
def test_update_task(mock_log_activity, client, auth_headers):
    # 1. Create a task first so we have something to update
    payload = {"title": "Original Title", "priority": "low"}
    post_res = client.post('/api/tasks/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    task_id = post_res.get_json()["id"]

    # 2. Update that specific task
    update_payload = {"title": "Updated Title", "status": "in_progress"}
    response = client.put(
        f'/api/tasks/{task_id}', 
        data=json.dumps(update_payload), 
        content_type='application/json', 
        headers=auth_headers
    )

    # 3. Assert the update was successful
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"
    
    # Assert DynamoDB was called for both the Create and Update actions
    assert mock_log_activity.call_count == 2 

@patch('app.services.task_service.dynamo_service.log_activity')
def test_delete_task(mock_log_activity, client, auth_headers):
    # 1. Create a task to delete
    payload = {"title": "Task to Delete"}
    post_res = client.post('/api/tasks/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    task_id = post_res.get_json()["id"]

    # 2. Delete the task
    response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)

    # 3. Assert it was deleted successfully
    assert response.status_code == 200
    assert response.get_json()["message"] == "Task soft deleted successfully"

    # 4. Verify we can no longer fetch it
    get_res = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
    assert get_res.status_code == 404