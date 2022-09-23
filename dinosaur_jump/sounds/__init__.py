from pathlib import Path

from base.sound import load_sound

folder = Path(__file__).parent

crowd_ohh = load_sound(folder / "crowd_ohh.wav")
hit = load_sound(folder / "hit.wav")
gunshot = load_sound(folder / "gunshot.wav")
