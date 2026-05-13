import pytest
from document_processor import DocumentProcessor


def write_course_file(tmp_path, content):
    f = tmp_path / "course.txt"
    f.write_text(content, encoding="utf-8")
    return str(f)


FULL_DOC = """\
Course Title: Python Fundamentals
Course Link: https://example.com/python
Course Instructor: Jane Doe

Lesson 1: Introduction to Python
Lesson Link: https://example.com/python/lesson1
Python is a versatile programming language. It was created in 1991. Python emphasizes readability.

Lesson 2: Variables and Data Types
Lesson Link: https://example.com/python/lesson2
Variables store data in Python. There are several data types available. Integers and strings are common.
"""

# Sentences chosen so A+B+C = 73 chars fit in chunk_size=80,
# but A+B+C+D = 101 exceeds it, producing two chunks with C as the overlap sentence.
_SENTENCES = (
    "Cats are great pets. "
    "Dogs are loyal companions. "
    "Fish are quiet creatures. "
    "Birds can sing beautifully."
)


# ---- chunk_text ----

def test_empty_string():
    dp = DocumentProcessor(chunk_size=200, chunk_overlap=0)
    assert dp.chunk_text("") == []


def test_whitespace_only():
    dp = DocumentProcessor(chunk_size=200, chunk_overlap=0)
    assert dp.chunk_text("   \n  ") == []


def test_single_short_sentence():
    dp = DocumentProcessor(chunk_size=200, chunk_overlap=0)
    result = dp.chunk_text("Hello world.")
    assert len(result) == 1
    assert result[0] == "Hello world."


def test_normalises_whitespace():
    dp = DocumentProcessor(chunk_size=200, chunk_overlap=0)
    result = dp.chunk_text("Hello   world.")
    assert result[0] == "Hello world."


def test_two_sentences_fit_one_chunk():
    dp = DocumentProcessor(chunk_size=200, chunk_overlap=0)
    result = dp.chunk_text("First sentence here. Second sentence here.")
    assert len(result) == 1
    assert "First sentence here." in result[0]
    assert "Second sentence here." in result[0]


def test_split_when_exceeds_chunk_size():
    dp = DocumentProcessor(chunk_size=80, chunk_overlap=0)
    chunks = dp.chunk_text(_SENTENCES)
    assert len(chunks) > 1


def test_long_single_sentence_still_emitted():
    dp = DocumentProcessor(chunk_size=20, chunk_overlap=0)
    long_sentence = "This is a very long sentence that exceeds the chunk size limit considerably."
    result = dp.chunk_text(long_sentence)
    assert len(result) == 1
    assert result[0] == long_sentence


def test_no_overlap_no_duplication():
    dp = DocumentProcessor(chunk_size=80, chunk_overlap=0)
    chunks = dp.chunk_text(_SENTENCES)
    assert len(chunks) > 1
    assert "Fish are quiet creatures." in chunks[0]
    assert "Fish are quiet creatures." not in chunks[1]


def test_overlap_repeats_tail_sentence():
    dp = DocumentProcessor(chunk_size=80, chunk_overlap=30)
    chunks = dp.chunk_text(_SENTENCES)
    assert len(chunks) > 1
    assert "Fish are quiet creatures." in chunks[0]
    assert chunks[1].startswith("Fish are quiet creatures.")


def test_all_chunks_nonempty():
    dp = DocumentProcessor(chunk_size=80, chunk_overlap=0)
    chunks = dp.chunk_text(_SENTENCES)
    for chunk in chunks:
        assert chunk != ""


def test_no_content_dropped():
    dp = DocumentProcessor(chunk_size=80, chunk_overlap=0)
    chunks = dp.chunk_text(_SENTENCES)
    input_words = set(_SENTENCES.replace(".", "").split())
    output_words = set(w.strip(".,!?") for chunk in chunks for w in chunk.split())
    assert input_words.issubset(output_words)


def test_punctuation_boundaries():
    dp = DocumentProcessor(chunk_size=200, chunk_overlap=0)
    text = "Stop right there! Now listen carefully. Are you ready? Yes I am ready."
    result = dp.chunk_text(text)
    combined = " ".join(result)
    assert "Stop right there" in combined
    assert "Now listen carefully" in combined
    assert "Are you ready" in combined
    assert "Yes I am ready" in combined


# ---- process_course_document ----

def test_returns_tuple(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    result = dp.process_course_document(path)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_parses_course_title(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, _ = dp.process_course_document(path)
    assert course.title == "Python Fundamentals"


def test_parses_course_link(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, _ = dp.process_course_document(path)
    assert course.course_link == "https://example.com/python"


def test_parses_instructor(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, _ = dp.process_course_document(path)
    assert course.instructor == "Jane Doe"


def test_missing_instructor_returns_none(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    doc = """\
Course Title: Python Fundamentals
Course Link: https://example.com/python

Lesson 1: Intro
Some content here for testing purposes only.
"""
    path = write_course_file(tmp_path, doc)
    course, _ = dp.process_course_document(path)
    assert course.instructor is None


def test_missing_link_returns_none(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    doc = """\
Course Title: Python Fundamentals
Course Instructor: Jane Doe

Lesson 1: Intro
Some content here for testing purposes only.
"""
    path = write_course_file(tmp_path, doc)
    course, _ = dp.process_course_document(path)
    assert course.course_link is None


def test_fallback_title_from_first_line(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    doc = """\
My Raw Title
Course Link: https://example.com

Lesson 1: Intro
Some content here for testing purposes only.
"""
    path = write_course_file(tmp_path, doc)
    course, _ = dp.process_course_document(path)
    assert course.title == "My Raw Title"


def test_lesson_count(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, _ = dp.process_course_document(path)
    assert len(course.lessons) == 2


def test_lesson_numbers_and_titles(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, _ = dp.process_course_document(path)
    assert course.lessons[0].lesson_number == 1
    assert course.lessons[0].title == "Introduction to Python"
    assert course.lessons[1].lesson_number == 2
    assert course.lessons[1].title == "Variables and Data Types"


def test_lesson_link_parsed(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, chunks = dp.process_course_document(path)
    assert course.lessons[0].lesson_link == "https://example.com/python/lesson1"
    lesson1_chunks = [c for c in chunks if c.lesson_number == 1]
    assert all(c.lesson_link == "https://example.com/python/lesson1" for c in lesson1_chunks)


def test_lesson_link_absent(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    doc = """\
Course Title: Python Fundamentals
Course Link: https://example.com/python
Course Instructor: Jane Doe

Lesson 1: Intro Without Link
Some content here.

Lesson 2: Second Lesson
More content here for the second lesson.
"""
    path = write_course_file(tmp_path, doc)
    course, _ = dp.process_course_document(path)
    assert course.lessons[0].lesson_link is None


def test_chunks_created(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    _, chunks = dp.process_course_document(path)
    assert len(chunks) >= 1


def test_chunk_index_sequential(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    _, chunks = dp.process_course_document(path)
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_chunk_course_title_propagated(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, chunks = dp.process_course_document(path)
    assert all(c.course_title == course.title for c in chunks)


def test_intermediate_lesson_first_chunk_prefix(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    _, chunks = dp.process_course_document(path)
    lesson1_chunks = [c for c in chunks if c.lesson_number == 1]
    assert lesson1_chunks[0].content.startswith("Lesson 1 content:")


def test_last_lesson_all_chunks_have_full_prefix(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    course, chunks = dp.process_course_document(path)
    lesson2_chunks = [c for c in chunks if c.lesson_number == 2]
    for chunk in lesson2_chunks:
        assert chunk.content.startswith(f"Course {course.title} Lesson 2 content:")


def test_no_lessons_fallback(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    doc = """\
Course Title: No Lessons Course
Course Link: https://example.com
Course Instructor: Jane Doe

This is a course without any lesson markers. It has some content. The content is parsed as one document.
"""
    path = write_course_file(tmp_path, doc)
    _, chunks = dp.process_course_document(path)
    assert len(chunks) >= 1
    assert all(c.lesson_number is None for c in chunks)


def test_lesson_link_not_in_chunk_content(tmp_path):
    dp = DocumentProcessor(chunk_size=800, chunk_overlap=100)
    path = write_course_file(tmp_path, FULL_DOC)
    _, chunks = dp.process_course_document(path)
    for chunk in chunks:
        assert "Lesson Link:" not in chunk.content
        assert "https://example.com/python/lesson1" not in chunk.content
        assert "https://example.com/python/lesson2" not in chunk.content
