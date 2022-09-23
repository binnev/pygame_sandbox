from pathlib import Path

from base.sound import load_sound

folder = Path(__file__).parent

applause = load_sound(folder / "applause.wav")
crowd_ohh = load_sound(folder / "crowd_ohh.wav")
crowd_cheer = load_sound(folder / "crowd_cheer.wav")
bullet_hit = load_sound(folder / "break.wav")
hit = load_sound(folder / "hit.wav")
gunshot = load_sound(folder / "gunshot.wav")
gun_click = load_sound(folder / "gun_click.wav")
eagle = load_sound(folder / "eagle.wav")
revolver_spin = load_sound(folder / "revolver-spin.wav", volume=1)
