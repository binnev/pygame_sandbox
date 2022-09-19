import random


def should_spawn(cooldown: int, current: int) -> bool:
    """
    Decide semi-randomly whether to spawn something. Cooldown is the maximum number of ticks
    between spawns. Current is the elapsed ticks. When current == cooldown, return True.
    Before that, use random chance.
    """
    return current >= random.randint(1, cooldown)
