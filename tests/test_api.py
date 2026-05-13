import pytest
from models import SourceItem


class TestQueryEndpoint:

    def test_returns_200_with_valid_query(self, api_client):
        response = api_client.post("/api/query", json={"query": "What is Python?"})
        assert response.status_code == 200

    def test_response_has_required_fields(self, api_client):
        data = api_client.post("/api/query", json={"query": "test"}).json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data

    def test_answer_from_rag_system(self, api_client):
        data = api_client.post("/api/query", json={"query": "test"}).json()
        assert data["answer"] == "Test answer"

    def test_creates_session_when_none_provided(self, api_client, mock_rag_system):
        response = api_client.post("/api/query", json={"query": "test"})
        mock_rag_system.session_manager.create_session.assert_called_once()
        assert response.json()["session_id"] == "session_1"

    def test_uses_provided_session_id(self, api_client, mock_rag_system):
        response = api_client.post(
            "/api/query", json={"query": "test", "session_id": "my-session"}
        )
        mock_rag_system.session_manager.create_session.assert_not_called()
        mock_rag_system.query.assert_called_once_with("test", "my-session")
        assert response.json()["session_id"] == "my-session"

    def test_sources_serialised_in_response(self, api_client, mock_rag_system):
        mock_rag_system.query.return_value = (
            "Answer",
            [SourceItem(text="Python basics", url="https://example.com/py")],
        )
        sources = api_client.post("/api/query", json={"query": "test"}).json()["sources"]
        assert len(sources) == 1
        assert sources[0]["text"] == "Python basics"
        assert sources[0]["url"] == "https://example.com/py"

    def test_source_with_no_url(self, api_client, mock_rag_system):
        mock_rag_system.query.return_value = (
            "Answer",
            [SourceItem(text="Some lesson", url=None)],
        )
        source = api_client.post("/api/query", json={"query": "test"}).json()["sources"][0]
        assert source["url"] is None

    def test_missing_query_field_returns_422(self, api_client):
        response = api_client.post("/api/query", json={})
        assert response.status_code == 422

    def test_non_object_body_returns_422(self, api_client):
        response = api_client.post("/api/query", json=["not", "an", "object"])
        assert response.status_code == 422

    def test_rag_error_returns_500(self, api_client, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("DB failure")
        response = api_client.post("/api/query", json={"query": "test"})
        assert response.status_code == 500

    def test_error_detail_in_500_response(self, api_client, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("DB failure")
        detail = api_client.post("/api/query", json={"query": "test"}).json()["detail"]
        assert "DB failure" in detail


class TestCoursesEndpoint:

    def test_returns_200(self, api_client):
        assert api_client.get("/api/courses").status_code == 200

    def test_total_courses_in_response(self, api_client):
        assert api_client.get("/api/courses").json()["total_courses"] == 2

    def test_course_titles_in_response(self, api_client):
        titles = api_client.get("/api/courses").json()["course_titles"]
        assert titles == ["Course A", "Course B"]

    def test_empty_catalog(self, api_client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": [],
        }
        data = api_client.get("/api/courses").json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_analytics_error_returns_500(self, api_client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("Analytics error")
        assert api_client.get("/api/courses").status_code == 500

    def test_analytics_calls_rag_system(self, api_client, mock_rag_system):
        api_client.get("/api/courses")
        mock_rag_system.get_course_analytics.assert_called_once()
