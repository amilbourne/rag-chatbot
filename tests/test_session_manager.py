import pytest
from session_manager import SessionManager


def test_create_session_returns_string():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    assert isinstance(sid, str)


def test_create_session_ids_are_unique():
    sm = SessionManager(max_history=3)
    assert sm.create_session() != sm.create_session()


def test_create_session_ids_are_sequential():
    sm = SessionManager(max_history=3)
    sid1 = sm.create_session()
    sid2 = sm.create_session()
    assert sid1 == "session_1"
    assert sid2 == "session_2"


def test_session_starts_empty():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    assert len(sm.sessions[sid]) == 0


def test_add_message_stores_role_and_content():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_message(sid, "user", "hello")
    msg = sm.sessions[sid][0]
    assert msg.role == "user"
    assert msg.content == "hello"


def test_add_message_unknown_session_auto_creates():
    sm = SessionManager(max_history=3)
    sm.add_message("ghost_session", "user", "hi")
    assert "ghost_session" in sm.sessions
    assert sm.sessions["ghost_session"][0].content == "hi"


def test_add_message_at_limit_no_trim():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    limit = sm.max_history * 2  # 6
    for i in range(limit):
        sm.add_message(sid, "user", f"msg_{i}")
    assert len(sm.sessions[sid]) == limit


def test_add_message_over_limit_trims_oldest():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    for i in range(sm.max_history * 2 + 1):  # 7 messages
        sm.add_message(sid, "user", f"msg_{i}")
    assert len(sm.sessions[sid]) == sm.max_history * 2


def test_add_message_trims_to_newest():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    for i in range(sm.max_history * 2 + 1):  # 7 messages: msg_0 through msg_6
        sm.add_message(sid, "user", f"msg_{i}")
    assert sm.sessions[sid][0].content == "msg_1"


def test_add_exchange_adds_two_messages():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_exchange(sid, "question", "answer")
    assert len(sm.sessions[sid]) == 2


def test_add_exchange_roles():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_exchange(sid, "question", "answer")
    assert sm.sessions[sid][0].role == "user"
    assert sm.sessions[sid][1].role == "assistant"


def test_add_exchange_content_preserved():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_exchange(sid, "my question", "my answer")
    assert sm.sessions[sid][0].content == "my question"
    assert sm.sessions[sid][1].content == "my answer"


def test_get_history_none_for_none_id():
    sm = SessionManager(max_history=3)
    assert sm.get_conversation_history(None) is None


def test_get_history_none_for_unknown_id():
    sm = SessionManager(max_history=3)
    assert sm.get_conversation_history("nonexistent") is None


def test_get_history_none_for_empty_session():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    assert sm.get_conversation_history(sid) is None


def test_get_history_user_line_format():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_message(sid, "user", "hello there")
    history = sm.get_conversation_history(sid)
    assert "User: hello there" in history


def test_get_history_assistant_line_format():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_message(sid, "assistant", "hi back")
    history = sm.get_conversation_history(sid)
    assert "Assistant: hi back" in history


def test_get_history_messages_joined_by_newline():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_exchange(sid, "question", "answer")
    history = sm.get_conversation_history(sid)
    lines = history.split("\n")
    assert len(lines) == 2
    assert all(line != "" for line in lines)


def test_clear_session_empties_messages():
    sm = SessionManager(max_history=3)
    sid = sm.create_session()
    sm.add_exchange(sid, "q", "a")
    sm.clear_session(sid)
    assert sid in sm.sessions
    assert len(sm.sessions[sid]) == 0


def test_clear_session_unknown_id_no_error():
    sm = SessionManager(max_history=3)
    sm.clear_session("does_not_exist")  # should not raise
