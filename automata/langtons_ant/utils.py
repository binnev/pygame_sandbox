import random


def random_ants(n: int):
    ants = []
    num_colours = 0
    for _ in range(n):
        x = random.randint(-10, 10)
        y = random.randint(-10, 10)
        rule_length = random.randint(2, 32)
        ruleset = "".join(random.choice("rl") for _ in range(rule_length))
        num_colours = max(num_colours, len(ruleset))
        ants.append(((x, y), ruleset, 0))
    return ants, num_colours
