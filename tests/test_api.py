"""Tests for the High School Management System API"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_has_expected_activities(self, client):
        """Test that GET /activities returns expected activity names"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Swimming Club", "Drama Club",
            "Art Studio", "Debate Club", "Science Olympiad"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_fails(self, client):
        """Test that signing up twice with the same email fails"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity names"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student2@mergington.edu"
        )
        assert response.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_remove_participant_actually_removes(self, client):
        """Test that removal actually removes the participant from the activity"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/participants/{email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client):
        """Test that removing a non-existent participant fails"""
        email = "nonexistent@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_from_nonexistent_activity_fails(self, client):
        """Test that removing from a non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Club/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_participant_with_url_encoding(self, client):
        """Test removal with URL-encoded parameters"""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess%20Club/participants/{email}"
        )
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_signup_and_remove_workflow(self, client):
        """Test complete workflow: signup then remove"""
        email = "testworkflow@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]
        
        # Remove
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity]["participants"]
    
    def test_multiple_signups_different_activities(self, client):
        """Test that a user can sign up for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_join = ["Chess Club", "Programming Class", "Drama Club"]
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        response = client.get("/activities")
        all_activities = response.json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
    
    def test_participant_count_changes(self, client):
        """Test that participant counts change correctly"""
        activity = "Chess Club"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Add participant
        email = "counter@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
        
        response = client.get("/activities")
        after_signup_count = len(response.json()[activity]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Remove participant
        client.delete(f"/activities/{activity}/participants/{email}")
        
        response = client.get("/activities")
        after_removal_count = len(response.json()[activity]["participants"])
        assert after_removal_count == initial_count
