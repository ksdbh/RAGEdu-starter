from backend.app.db import CourseSyllabusStore


def test_course_store_in_memory_put_get():
    store = CourseSyllabusStore(table_name="test")
    course_id = "demo"
    course_payload = {"id": course_id, "title": "Demo Course", "description": "x"}
    assert store.create_course(course_id, course_payload) is True
    got = store.get_course(course_id)
    assert got["title"] == "Demo Course"

    syllabus = {"course_id": course_id, "weeks": [{"week": 1, "topics": ["t1"]}]}
    assert store.create_syllabus(course_id, syllabus) is True
    got_syl = store.get_syllabus(course_id)
    assert got_syl["weeks"][0]["topics"] == ["t1"]
