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
