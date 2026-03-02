import json
from unittest.mock import patch

# ==========================================
# PHASE 1 & 2: CORE CRUD TESTS
# ==========================================

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
    
    # 4. Verify that our code ATTEMPTED to call DynamoDB
    mock_log_activity.assert_called_once()

def test_get_tasks_unauthorized(client):
    response = client.get('/api/tasks/')
    assert response.status_code == 401

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


# ==========================================
# PHASE 3: ADVANCED OPERATIONS & ACTIVITIES TESTS
# ==========================================

@patch('app.services.task_service.dynamo_service.log_activity')
def test_task_stats(mock_log_activity, client, auth_headers):
    # 1. Create a couple of tasks to generate stats
    client.post('/api/tasks/', data=json.dumps({"title": "Stat Task 1", "status": "todo"}), content_type='application/json', headers=auth_headers)
    client.post('/api/tasks/', data=json.dumps({"title": "Stat Task 2", "status": "in_progress"}), content_type='application/json', headers=auth_headers)

    # 2. Fetch the stats
    response = client.get('/api/tasks/stats', headers=auth_headers)
    
    # 3. Assert the stats calculate correctly
    assert response.status_code == 200
    data = response.get_json()
    assert "total_tasks" in data
    assert "by_status" in data
    assert "by_priority" in data

@patch('app.services.task_service.dynamo_service.log_activity')
def test_search_tasks(mock_log_activity, client, auth_headers):
    # 1. Create a task with a very specific, searchable keyword
    payload = {"title": "FindThisSpecificWord Task", "description": "Hidden description"}
    client.post('/api/tasks/', data=json.dumps(payload), content_type='application/json', headers=auth_headers)

    # 2. Search for that keyword
    response = client.get('/api/tasks/search?q=FindThisSpecificWord', headers=auth_headers)
    
    # 3. Assert it found our exact task
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["tasks"]) >= 1
    assert data["tasks"][0]["title"] == "FindThisSpecificWord Task"

@patch('app.services.task_service.dynamo_service.log_activity')
def test_bulk_update_tasks(mock_log_activity, client, auth_headers):
    # 1. Create two tasks and grab their IDs
    t1 = client.post('/api/tasks/', data=json.dumps({"title": "Bulk 1"}), content_type='application/json', headers=auth_headers).get_json()
    t2 = client.post('/api/tasks/', data=json.dumps({"title": "Bulk 2"}), content_type='application/json', headers=auth_headers).get_json()

    # 2. Send the bulk update payload
    payload = {
        "task_ids": [t1["id"], t2["id"]],
        "update_data": {"status": "in_progress", "priority": "high"}
    }
    response = client.post('/api/tasks/bulk-update', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    assert response.status_code == 200

    # 3. Verify the first task actually changed in the database
    verify_res = client.get(f'/api/tasks/{t1["id"]}', headers=auth_headers).get_json()
    assert verify_res["status"] == "in_progress"
    assert verify_res["priority"] == "high"

@patch('app.services.task_service.dynamo_service.log_activity')
def test_bulk_delete_tasks(mock_log_activity, client, auth_headers):
    # 1. Create a task
    t1 = client.post('/api/tasks/', data=json.dumps({"title": "Bulk Delete Me"}), content_type='application/json', headers=auth_headers).get_json()

    # 2. Send the bulk delete payload
    payload = {"task_ids": [t1["id"]]}
    response = client.post('/api/tasks/bulk-delete', data=json.dumps(payload), content_type='application/json', headers=auth_headers)
    assert response.status_code == 200

    # 3. Verify it is now returning a 404 (soft deleted)
    verify_res = client.get(f'/api/tasks/{t1["id"]}', headers=auth_headers)
    assert verify_res.status_code == 404

@patch('app.services.dynamodb_service.DynamoDBService.get_activities')
def test_activities_endpoints(mock_get_activities, client, auth_headers):
    # 1. Mock DynamoDB returning a fake list of activities
    mock_get_activities.return_value = [
        {"action": "create", "task_id": "123", "ip_address": "192.168.1.1"},
        {"action": "create", "task_id": "456", "ip_address": "192.168.1.1"},
        {"action": "update", "task_id": "123", "ip_address": "192.168.1.1"}
    ]

    # 2. Test the standard list endpoint
    list_res = client.get('/api/activities/', headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.get_json()["activities"]) == 3

    # 3. Test the summary endpoint calculates totals correctly
    summary_res = client.get('/api/activities/summary', headers=auth_headers)
    assert summary_res.status_code == 200
    summary_data = summary_res.get_json()
    assert summary_data["total_activities"] == 3
    assert summary_data["summary"]["create"] == 2
    assert summary_data["summary"]["update"] == 1