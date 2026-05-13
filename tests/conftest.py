import sys
import pytest
from unittest.mock import MagicMock, patch
from vector_store import SearchResults


# ---- Unit-test fixtures (used by test_search_tools.py) ----

@pytest.fixture
def mock_store():
    store = MagicMock()
    store.search.return_value = SearchResults(documents=[], metadata=[], distances=[])
    store.get_lesson_link.return_value = None
    store.get_course_link.return_value = None
    return store


@pytest.fixture
def search_tool(mock_store):
    from search_tools import CourseSearchTool
    return CourseSearchTool(mock_store)


@pytest.fixture
def tool_manager(search_tool):
    from search_tools import ToolManager
    tm = ToolManager()
    tm.register_tool(search_tool)
    return tm


# ---- API test fixtures ----

class _FakeStaticFiles:
    """Drop-in for StaticFiles that skips the directory-existence check."""
    def __init__(self, *args, **kwargs):
        pass

    async def __call__(self, scope, receive, send):
        pass


@pytest.fixture(scope="session")
def app_module():
    """Import the FastAPI app once per session with StaticFiles and RAGSystem mocked."""
    with patch("fastapi.staticfiles.StaticFiles", _FakeStaticFiles), \
         patch("rag_system.RAGSystem"):
        sys.modules.pop("app", None)
        import app as _app
    return _app


@pytest.fixture
def mock_rag_system():
    """Fresh mock RAGSystem for each test, pre-configured with sane defaults."""
    m = MagicMock()
    m.session_manager.create_session.return_value = "session_1"
    m.query.return_value = ("Test answer", [])
    m.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Course A", "Course B"],
    }
    m.add_course_folder.return_value = (0, 0)
    return m


@pytest.fixture
def api_client(app_module, mock_rag_system):
    """TestClient wired to a fresh mock RAGSystem for each test."""
    app_module.rag_system = mock_rag_system
    from fastapi.testclient import TestClient
    return TestClient(app_module.app)
