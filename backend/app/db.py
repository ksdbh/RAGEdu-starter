import time
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger("db")


class DynamoDBRecorder:
    """Best-effort recorder for quiz results to DynamoDB.

    This class attempts to put items into a DynamoDB table named 'RAGEduQuizResults'.
    If AWS credentials or network are not available, record() will catch exceptions
    and return False. This keeps the scaffold safe to run locally without AWS.
    """

    def __init__(self, table_name: str = "RAGEduQuizResults"):
        self.table_name = table_name
        try:
            self.client = boto3.client("dynamodb")
        except Exception as e:
            logger.info("DynamoDB client not available: %s", e)
            self.client = None

    def record(self, item: Dict[str, Any]) -> bool:
        """Put a single result item into the DynamoDB table.

        The function will coerce values into DynamoDB expected types using the
        AttributeValue shape (strings/numbers). It attaches a timestamp.
        Returns True if the put succeeded, False otherwise.
        """
        ts = int(time.time())
        payload = {"quiz_id": {"S": str(item.get("quiz_id"))},
                   "question_id": {"S": str(item.get("question_id"))},
                   "timestamp": {"N": str(ts)},
                   "correct": {"BOOL": bool(item.get("correct", False))}}

        if item.get("user_id") is not None:
            payload["user_id"] = {"S": str(item.get("user_id"))}
        if item.get("response") is not None:
            payload["response"] = {"S": str(item.get("response"))}
        if item.get("time_ms") is not None:
            # number
            try:
                payload["time_ms"] = {"N": str(int(item.get("time_ms")))}
            except Exception:
                pass

        if not self.client:
            logger.info("DynamoDB client not configured; skipping record: %s", payload)
            return False

        try:
            self.client.put_item(TableName=self.table_name, Item=payload)
            logger.info("Recorded quiz result to %s", self.table_name)
            return True
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to record to DynamoDB: %s", e)
            return False
        except Exception as e:
            logger.exception("Unexpected error recording to DynamoDB: %s", e)
            return False


# -------------------------
# Course / Syllabus store
# -------------------------

import json


class CourseSyllabusStore:
    """Best-effort store for Course and Syllabus objects in DynamoDB.

    This provides a minimal API used by the scaffold to create and fetch course
    metadata and syllabi. When a real DynamoDB client is not available we fall
    back to an in-memory dictionary so local dev and unit tests are deterministic.

    Items are stored in a table (default 'RAGEduCourses') using a simple PK and
    a JSON-serialized payload under attribute 'payload'.
    """

    def __init__(self, table_name: str = "RAGEduCourses"):
        self.table_name = table_name
        try:
            self.client = boto3.client("dynamodb")
        except Exception as e:
            logger.info("DynamoDB client not available for CourseSyllabusStore: %s", e)
            self.client = None
        # in-memory fallback store: key -> dict payload
        self._store: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, course_id: str, kind: str) -> str:
        return f"{course_id}#{kind}"

    def create_course(self, course_id: str, payload: Dict[str, Any]) -> bool:
        key = self._make_key(course_id, "course")
        return self._put(key, payload)

    def get_course(self, course_id: str) -> Dict[str, Any]:
        key = self._make_key(course_id, "course")
        return self._get(key)

    def create_syllabus(self, course_id: str, payload: Dict[str, Any]) -> bool:
        key = self._make_key(course_id, "syllabus")
        return self._put(key, payload)

    def get_syllabus(self, course_id: str) -> Dict[str, Any]:
        key = self._make_key(course_id, "syllabus")
        return self._get(key)

    def _put(self, key: str, payload: Dict[str, Any]) -> bool:
        if not self.client:
            # in-memory store
            self._store[key] = payload
            logger.info("Stored item in in-memory CourseSyllabusStore: %s", key)
            return True

        try:
            doc = {"id": {"S": key}, "payload": {"S": json.dumps(payload)}}
            self.client.put_item(TableName=self.table_name, Item=doc)
            logger.info("Stored item to DynamoDB table %s key=%s", self.table_name, key)
            return True
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to put_item to DynamoDB for %s: %s", key, e)
            return False
        except Exception as e:
            logger.exception("Unexpected error storing %s: %s", key, e)
            return False

    def _get(self, key: str) -> Dict[str, Any]:
        if not self.client:
            v = self._store.get(key)
            if v is None:
                raise KeyError(key)
            return v

        try:
            res = self.client.get_item(TableName=self.table_name, Key={"id": {"S": key}})
            item = res.get("Item")
            if not item:
                raise KeyError(key)
            payload_s = item.get("payload", {}).get("S")
            if not payload_s:
                raise KeyError(key)
            return json.loads(payload_s)
        except (BotoCoreError, ClientError) as e:
            logger.exception("Failed to get_item from DynamoDB for %s: %s", key, e)
            raise
        except Exception as e:
            logger.exception("Unexpected error retrieving %s: %s", key, e)
            raise
