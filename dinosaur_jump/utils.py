import random


def should_spawn(cooldown: int, tick: int, chance: float) -> bool:
    """
    Decide semi-randomly whether to spawn something. Cooldown is the maximum number of ticks
    between spawns. Current is the elapsed ticks. When tick == cooldown, return True.
    Before that, use random chance.
    """
    if tick < cooldown:
        return False

    return random.random() < chance
