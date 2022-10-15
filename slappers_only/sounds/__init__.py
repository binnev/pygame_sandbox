from pathlib import Path

from robingame.sound import load_sound

folder = Path(__file__).parent

metal_clang = load_sound(folder / "metal_clang.wav")
slap1 = load_sound(folder / "slap1.wav")
slap2 = load_sound(folder / "slap2.wav")
slap3 = load_sound(folder / "slap3.wav")
slap4 = load_sound(folder / "slap4.wav")
slap5 = load_sound(folder / "slap5.wav")
