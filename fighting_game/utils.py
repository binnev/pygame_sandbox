from math import sin


def pulsing_value(tick, min, max, freq, func=None):
    func = func if func else sin
    A = (max - min) / 2
    B = (max + min) / 2
    return A * func(tick * freq) + B
