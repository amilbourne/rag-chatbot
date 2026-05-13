import pytest
from unittest.mock import MagicMock
from search_tools import CourseSearchTool, ToolManager
from vector_store import SearchResults


def one_result(mock_store, course_title="MyCourse", lesson_number=1,
               doc_text="Some content.", lesson_link=None, course_link=None):
    mock_store.search.return_value = SearchResults(
        documents=[doc_text],
        metadata=[{"course_title": course_title, "lesson_number": lesson_number}],
        distances=[0.1],
    )
    mock_store.get_lesson_link.return_value = lesson_link
    mock_store.get_course_link.return_value = course_link


# ---- CourseSearchTool ----

def test_calls_store_search_once(search_tool, mock_store):
    search_tool.execute(query="python basics")
    mock_store.search.assert_called_once()


def test_passes_query(search_tool, mock_store):
    search_tool.execute(query="python basics")
    assert mock_store.search.call_args.kwargs["query"] == "python basics"


def test_passes_course_name_and_lesson(search_tool, mock_store):
    search_tool.execute(query="types", course_name="Python", lesson_number=2)
    kwargs = mock_store.search.call_args.kwargs
    assert kwargs["course_name"] == "Python"
    assert kwargs["lesson_number"] == 2


def test_returns_string(search_tool):
    result = search_tool.execute(query="test")
    assert isinstance(result, str)


def test_header_with_course_and_lesson(search_tool, mock_store):
    one_result(mock_store, course_title="MyCourse", lesson_number=2)
    result = search_tool.execute(query="test")
    assert "[MyCourse - Lesson 2]" in result


def test_header_without_lesson(search_tool, mock_store):
    one_result(mock_store, course_title="MyCourse", lesson_number=None)
    result = search_tool.execute(query="test")
    assert "[MyCourse]" in result
    assert "[MyCourse - Lesson" not in result


def test_populates_last_sources(search_tool, mock_store):
    one_result(mock_store)
    search_tool.execute(query="test")
    assert len(search_tool.last_sources) > 0


def test_source_uses_lesson_link(search_tool, mock_store):
    one_result(mock_store, lesson_link="https://example.com/lesson1")
    search_tool.execute(query="test")
    assert search_tool.last_sources[0].url == "https://example.com/lesson1"


def test_source_falls_back_to_course_link(search_tool, mock_store):
    one_result(mock_store, lesson_link=None, course_link="https://example.com/course")
    search_tool.execute(query="test")
    assert search_tool.last_sources[0].url == "https://example.com/course"


def test_source_url_none_when_no_links(search_tool, mock_store):
    one_result(mock_store, lesson_link=None, course_link=None)
    search_tool.execute(query="test")
    assert search_tool.last_sources[0].url is None


def test_deduplicates_sources(search_tool, mock_store):
    mock_store.search.return_value = SearchResults(
        documents=["content A", "content B"],
        metadata=[
            {"course_title": "Python", "lesson_number": 1},
            {"course_title": "Python", "lesson_number": 1},
        ],
        distances=[0.1, 0.2],
    )
    mock_store.get_lesson_link.return_value = "https://example.com/lesson1"
    search_tool.execute(query="test")
    assert len(search_tool.last_sources) == 1


def test_second_call_returns_limit_message(search_tool, mock_store):
    one_result(mock_store)
    search_tool.execute(query="first")
    result = search_tool.execute(query="second")
    assert "Search limit reached" in result


def test_second_call_does_not_call_store_again(search_tool, mock_store):
    one_result(mock_store)
    search_tool.execute(query="first")
    search_tool.execute(query="second")
    mock_store.search.assert_called_once()


def test_empty_results_message(search_tool):
    result = search_tool.execute(query="anything")
    assert "No relevant content found" in result


def test_empty_results_includes_course_filter(search_tool):
    result = search_tool.execute(query="anything", course_name="DataScience")
    assert "DataScience" in result


def test_empty_results_includes_lesson_filter(search_tool):
    result = search_tool.execute(query="anything", lesson_number=3)
    assert "3" in result


def test_error_result_returned_verbatim(search_tool, mock_store):
    mock_store.search.return_value = SearchResults(
        documents=[], metadata=[], distances=[], error="DB connection failed"
    )
    result = search_tool.execute(query="test")
    assert result == "DB connection failed"


def test_search_count_increments(search_tool):
    assert search_tool._search_count == 0
    search_tool.execute(query="test")
    assert search_tool._search_count == 1


def test_tool_definition_keys(search_tool):
    defn = search_tool.get_tool_definition()
    assert "name" in defn
    assert "description" in defn
    assert "input_schema" in defn


def test_tool_definition_name(search_tool):
    assert search_tool.get_tool_definition()["name"] == "search_course_content"


def test_tool_definition_query_required(search_tool):
    defn = search_tool.get_tool_definition()
    assert "query" in defn["input_schema"]["required"]


# ---- ToolManager ----

def test_register_and_execute(tool_manager, mock_store):
    one_result(mock_store)
    result = tool_manager.execute_tool("search_course_content", query="test")
    assert isinstance(result, str)
    assert mock_store.search.called


def test_register_raises_for_missing_name():
    from search_tools import Tool

    class NamelessTool(Tool):
        def get_tool_definition(self):
            return {}
        def execute(self, **kwargs):
            return ""

    tm = ToolManager()
    with pytest.raises(ValueError):
        tm.register_tool(NamelessTool())


def test_get_tool_definitions_returns_list(tool_manager):
    assert isinstance(tool_manager.get_tool_definitions(), list)


def test_get_tool_definitions_length(tool_manager):
    assert len(tool_manager.get_tool_definitions()) == 1


def test_execute_unknown_tool_returns_error(tool_manager):
    result = tool_manager.execute_tool("bogus_tool")
    assert "not found" in result.lower() or "bogus_tool" in result


def test_get_last_sources_empty_before_search(tool_manager):
    assert tool_manager.get_last_sources() == []


def test_get_last_sources_after_search(tool_manager, mock_store):
    one_result(mock_store, lesson_link="https://example.com")
    tool_manager.execute_tool("search_course_content", query="test")
    sources = tool_manager.get_last_sources()
    assert len(sources) > 0


def test_reset_sources_clears(tool_manager, mock_store):
    one_result(mock_store)
    tool_manager.execute_tool("search_course_content", query="test")
    tool_manager.reset_sources()
    assert tool_manager.get_last_sources() == []


def test_reset_sources_resets_search_count(tool_manager, search_tool, mock_store):
    one_result(mock_store)
    search_tool.execute(query="first")  # increments _search_count to 1
    tool_manager.reset_sources()
    result = search_tool.execute(query="second")
    assert "Search limit reached" not in result


def test_multiple_tools_definitions():
    from search_tools import Tool

    class FakeTool(Tool):
        def __init__(self, name):
            self._name = name
        def get_tool_definition(self):
            return {"name": self._name, "description": "test", "input_schema": {}}
        def execute(self, **kwargs):
            return ""

    tm = ToolManager()
    tm.register_tool(FakeTool("tool_one"))
    tm.register_tool(FakeTool("tool_two"))
    assert len(tm.get_tool_definitions()) == 2
