# backend/app/db.py
from __future__ import annotations

import os
from typing import Dict, Any, Optional


class CourseSyllabusStore:
    """
    Very small store that defaults to in-memory for CI.
    If AWS/LocalStack is available, you can extend this to use boto3.
    """
    _mem: Dict[str, Dict[str, Any]] = {}

    def __init__(self, table_name: str = "courses"):
        self.table_name = table_name
        self.use_memory = os.environ.get("USE_IN_MEMORY_DB", "1") == "1"
        self.client = None
        if not self.use_memory:
            try:
                import boto3  # type: ignore
                endpoint_url = os.environ.get("AWS_ENDPOINT_URL") or os.environ.get("AWS_ENDPOINT_URL_S3")
                self.client = boto3.client("dynamodb", endpoint_url=endpoint_url) if endpoint_url else boto3.client("dynamodb")
            except Exception:
                # Fall back to memory if boto3 not available
                self.use_memory = True

    def _key(self, course_id: str) -> str:
        return f"{course_id}#course"

    def create_course(self, course_id: str, payload: Dict[str, Any]) -> bool:
        if self.use_memory or not self.client:
            key = self._key(course_id)
            self._mem[key] = dict(payload)
            return True
        # (Optional) Real DynamoDB path could go here; for tests, memory is enough.
        try:
            doc = {"pk": {"S": self._key(course_id)}, "doc": {"S": str(payload)}}
            self.client.put_item(TableName=self.table_name, Item=doc)
            return True
        except Exception:
            return False

    def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        if self.use_memory or not self.client:
            return self._mem.get(self._key(course_id))
        try:
            res = self.client.get_item(TableName=self.table_name, Key={"pk": {"S": self._key(course_id)}})
            item = res.get("Item")
            if not item:
                return None
            return {"raw": item.get("doc", {}).get("S")}
        except Exception:
            return None