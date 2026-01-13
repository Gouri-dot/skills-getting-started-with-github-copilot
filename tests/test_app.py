"""
Tests for the FastAPI activities application
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a clean state before each test"""
    # Store original state
    original_activities = {
        "Basketball Team": {
            "description": "Join the basketball team and compete in local tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Practice soccer skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create projects",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Society": {
            "description": "Participate in theater productions and improve acting skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Club": {
            "description": "Engage in debates and improve public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    }
    
    # Import activities from app module
    from app import activities
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Should contain all activities
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Club" in data
        assert len(data) == 9
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that each activity has the expected structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_returns_participants(self, client, reset_activities):
        """Test that activities with participants return them"""
        response = client.get("/activities")
        data = response.json()
        
        # Check activities that have pre-populated participants
        assert isinstance(data["Chess Club"]["participants"], list)
        assert isinstance(data["Programming Class"]["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "student@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """Test that duplicate signup returns 400"""
        email = "student@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Duplicate signup
        response2 = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                "/activities/Basketball%20Team/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Basketball Team"]["participants"]
        assert len(data["Basketball Team"]["participants"]) == 3


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity"""
        email = "student@mergington.edu"
        
        # Sign up first
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        
        # Unregister
        response = client.delete(
            "/activities/Basketball%20Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "student@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        
        # Unregister
        client.delete(
            "/activities/Basketball%20Team/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball Team"]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up_returns_400(self, client, reset_activities):
        """Test that unregister for non-participant returns 400"""
        response = client.delete(
            "/activities/Basketball%20Team/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_one_of_multiple(self, client, reset_activities):
        """Test unregistering one student when multiple are signed up"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Sign up all
        for email in emails:
            client.post(
                "/activities/Basketball%20Team/signup",
                params={"email": email}
            )
        
        # Unregister one
        client.delete(
            "/activities/Basketball%20Team/unregister",
            params={"email": emails[1]}
        )
        
        # Verify only that one was removed
        response = client.get("/activities")
        data = response.json()
        assert emails[0] in data["Basketball Team"]["participants"]
        assert emails[1] not in data["Basketball Team"]["participants"]
        assert emails[2] in data["Basketball Team"]["participants"]
        assert len(data["Basketball Team"]["participants"]) == 2


class TestIntegration:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test a complete signup and unregister workflow"""
        email = "student@mergington.edu"
        activity = "Basketball Team"
        
        # Verify initially not signed up
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
        # Sign up
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
