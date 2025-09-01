from backend.app.quests import topics_to_quests, build_quest_map


def test_topics_to_quests_generates_three_per_topic():
    topics = ["Intro to Graphs", "Shortest Paths"]
    quests = topics_to_quests(1, topics, course_id="c1")
    # Each topic should expand to 3 quests (read, quiz, apply)
    assert len(quests) == 6
    types = [q["type"] for q in quests]
    # Expect pattern read, quiz, apply repeated
    assert types[0:3] == ["read", "quiz", "apply"]
    assert types[3:6] == ["read", "quiz", "apply"]
    # ids should be deterministic and unique
    ids = [q["id"] for q in quests]
    assert len(set(ids)) == 6


def test_build_quest_map_from_syllabus_structure():
    syllabus = {"weeks": [{"week": 1, "topics": ["A"]}, {"week": 2, "topics": ["B", "C"]}]}
    qm = build_quest_map(syllabus, course_id="course42")
    assert qm["course_id"] == "course42"
    assert len(qm["weeks"]) == 2
    assert qm["weeks"][0]["week"] == 1
    assert len(qm["weeks"][0]["quests"]) == 3
    assert qm["weeks"][1]["week"] == 2
    assert len(qm["weeks"][1]["quests"]) == 6
