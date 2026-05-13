import pytest
from unittest.mock import MagicMock
from vector_store import SearchResults


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
