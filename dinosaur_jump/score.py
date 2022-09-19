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

    def save(self):
        scores = load_scores()
        scores.append(self)
        save_scores(scores)


def save_scores(scores: list[Score]):
    scores = [s.to_dict() for s in scores]
    with open(filename, "w") as file:
        json.dump(scores, file)


def load_scores() -> list[Score]:
    if filename.exists():
        with open(filename) as file:
            contents = file.read()
        if contents:
            scores = json.loads(contents)
            return [Score.from_dict(s) for s in scores]

    return []


def highscores() -> list[Score]:
    return list(sorted(load_scores(), key=lambda s: -s.score))[:10]


def is_highscore(score: int) -> bool:
    scores = highscores()
    if len(scores) < 10:
        return True
    print(scores)
    if score > scores[-1].score:
        return True
