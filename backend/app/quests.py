from typing import List, Dict, Optional
import hashlib


def _id_for(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"q_{h}"


def topics_to_quests(week_number: int, topics: List[str], course_id: Optional[str] = None) -> List[Dict]:
    """Transform a list of topics for a single week into three quests per topic:

    For each provided topic we generate three compact quests: read, quiz, apply.
    The function is deterministic (sha256-based ids) so tests/local runs are stable.
    """
    quests: List[Dict] = []
    for t in topics:
        base = t.strip()
        if not base:
            continue

        # Read quest
        read_title = f"Read: {base}"
        read_desc = f"Skim the recommended readings and notes for '{base}' to build baseline understanding."
        read_id = _id_for(f"{week_number}|read|{course_id}|{base}")

        # Quiz quest
        quiz_title = f"Quick Quiz: {base}"
        quiz_desc = f"Take a short formative quiz to check recall and key facts about '{base}'."
        quiz_id = _id_for(f"{week_number}|quiz|{course_id}|{base}")

        # Apply quest
        apply_title = f"Apply: {base}"
        apply_desc = f"Hands-on exercise or mini-project to apply concepts from '{base}'."
        apply_id = _id_for(f"{week_number}|apply|{course_id}|{base}")

        quests.extend([
            {
                "id": read_id,
                "type": "read",
                "title": read_title,
                "description": read_desc,
                "estimated_minutes": 20,
                "week": week_number,
                "topic": base,
            },
            {
                "id": quiz_id,
                "type": "quiz",
                "title": quiz_title,
                "description": quiz_desc,
                "estimated_minutes": 10,
                "week": week_number,
                "topic": base,
            },
            {
                "id": apply_id,
                "type": "apply",
                "title": apply_title,
                "description": apply_desc,
                "estimated_minutes": 30,
                "week": week_number,
                "topic": base,
            },
        ])

    return quests


def build_quest_map(syllabus: Dict, course_id: Optional[str] = None) -> Dict:
    """Given a syllabus payload (dict with 'weeks' list), build a quest-map.

    Expected syllabus format:
    {
      "weeks": [ {"week": 1, "topics": ["t1","t2"]}, ... ]
    }

    Returns a dict: {"course_id": ..., "weeks": [ {"week": n, "quests": [...]}, ... ] }
    """
    result = {"course_id": course_id, "weeks": []}
    weeks = syllabus.get("weeks") or []
    for w in weeks:
        week_num = w.get("week")
        topics = w.get("topics") or []
        quests = topics_to_quests(week_num, topics, course_id=course_id)
        result["weeks"].append({"week": week_num, "quests": quests})
    return result
