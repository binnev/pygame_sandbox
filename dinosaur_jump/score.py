import termios
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import json
from dataclasses_json import dataclass_json


filename = Path(__file__).parent / "high-scores.json"


@dataclass_json
@dataclass
class Score:
    score: int
    name: str = "anonymous"
    date: str = datetime.now().date().isoformat()

    def __repr__(self):
        return f"Score(score={self.score}, name={self.name}, date={self.date})"


def save_scores(scores: list[Score]):
    scores = [s.to_dict() for s in scores]
    with open(filename, "w") as file:
        json.dump(scores, file)


def load_scores() -> list[Score]:
    with open(filename) as file:
        scores = json.load(file)
    return [Score.from_dict(s) for s in scores]
