"""
API endpoint tests using the AAA (Arrange-Act-Assert) pattern.

Each test follows the structure:
- Arrange: Set up necessary data and state
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test: GET /activities returns all available activities
        
        Arrange: Client is ready from fixture
        Act: Make GET request to /activities
        Assert: Status is 200 and response contains activities
        """
        # Arrange - done by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_has_required_fields(self, client):
        """
        Test: Each activity has required fields (description, schedule, max_participants, participants)
        
        Arrange: Client is ready
        Act: Make GET request and extract an activity
        Assert: All required fields exist with correct types
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        first_activity = next(iter(activities.values()))
        
        # Assert
        for field in required_fields:
            assert field in first_activity, f"Missing field: {field}"
        assert isinstance(first_activity["participants"], list)
        assert isinstance(first_activity["max_participants"], int)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_adds_participant(self, client):
        """
        Test: Successfully signing up adds email to activity participants
        
        Arrange: Select an activity and new email
        Act: POST signup request
        Assert: Response is 200 and returns success message
        """
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_duplicate_returns_400_error(self, client):
        """
        Test: Attempting to sign up twice returns 400 error
        
        Arrange: Select an existing participant
        Act: Try to POST signup with already-registered email
        Assert: Response is 400 with appropriate error message
        """
        # Arrange
        activity = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test: Signing up for non-existent activity returns 404
        
        Arrange: Prepare request with fake activity name
        Act: POST signup to nonexistent activity
        Assert: Response is 404 with "Activity not found" message
        """
        # Arrange
        fake_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_to_full_activity_returns_400(self, client):
        """
        Test: Signing up to a full activity returns 400 error
        
        Arrange: Find or create an activity with no spots left
        Act: Try to sign up a new participant
        Assert: Response is 400 with "Activity is full" message
        """
        # Arrange
        # First, fill up an activity with small capacity
        activity = "Chess Club"  # max_participants: 12, currently has 2
        new_emails = [f"student{i}@mergington.edu" for i in range(10)]
        
        for email in new_emails:
            client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Try to sign up one more (should fail)
        final_email = "final@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": final_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_updates_participant_count(self, client):
        """
        Test: Successful signup increases participant count shown in activity
        
        Arrange: Get activities before signup
        Act: Sign up a new participant and get activities again
        Assert: Participant count increased by 1
        """
        # Arrange
        activity = "Programming Class"
        email = "newprogrammer@mergington.edu"
        
        before = client.get("/activities").json()
        before_count = len(before[activity]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        after = client.get("/activities").json()
        after_count = len(after[activity]["participants"])
        assert after_count == before_count + 1
        assert email in after[activity]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_participant_successful(self, client):
        """
        Test: Successfully removing a participant deletes them from activity
        
        Arrange: Select an existing participant
        Act: DELETE request for that participant
        Assert: Response is 200 with success message
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Test: Removing non-existent participant returns 404
        
        Arrange: Prepare request with email not in activity
        Act: DELETE request for non-existent participant
        Assert: Response is 404 with "Participant not found" message
        """
        # Arrange
        activity = "Gym Class"
        fake_email = "notamember@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{fake_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Test: Removing from non-existent activity returns 404
        
        Arrange: Prepare request with fake activity
        Act: DELETE request to nonexistent activity
        Assert: Response is 404 with "Activity not found" message
        """
        # Arrange
        fake_activity = "Fake Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_participant_decreases_count(self, client):
        """
        Test: Removing a participant decreases the participant count
        
        Arrange: Get activities before removal
        Act: Delete a participant and get activities again
        Assert: Participant count decreased by 1 and email is removed
        """
        # Arrange
        activity = "Gym Class"
        email = "john@mergington.edu"
        
        before = client.get("/activities").json()
        before_count = len(before[activity]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 200
        after = client.get("/activities").json()
        after_count = len(after[activity]["participants"])
        
        assert after_count == before_count - 1
        assert email not in after[activity]["participants"]

    def test_remove_and_signup_same_participant(self, client):
        """
        Test: After removing a participant, they can sign up again
        
        Arrange: Remove an existing participant
        Act: Sign them up again with a new POST request
        Assert: Both operations succeed and count is consistent
        """
        # Arrange
        activity = "Gym Class"
        email = "olivia@mergington.edu"
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Act - Re-signup
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert remove_response.status_code == 200
        assert signup_response.status_code == 200
        final = client.get("/activities").json()
        assert email in final[activity]["participants"]
