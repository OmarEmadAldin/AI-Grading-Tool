import json
from typing import Optional
from pathlib import Path

class MarkScheme:
    def __init__(self, question, max_score, marking_points, topic=None):
        self.question = question
        self.max_score = max_score
        self.marking_points = marking_points
        self.topic = topic

    def to_prompt_block(self) -> str:
        points = "\n".join(f"  - {p}" for p in self.marking_points)
        topic_line = f"Topic: {self.topic}\n" if self.topic else ""
        return (
            f"{topic_line}"
            f"Question: {self.question}\n"
            f"Max Score: {self.max_score}\n"
            f"Marking Points (each worth 1 mark):\n{points}"
        )


def load_mark_scheme(json_path: Optional[str] = None) -> MarkScheme:

    if json_path and Path(json_path).exists():
        with open(json_path) as f:
            data = json.load(f)
        return MarkScheme(
            question=data["question"],
            max_score=data["max_score"],
            marking_points=data["marking_points"],
            topic=data.get("topic"),
        )
