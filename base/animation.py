import numpy


def ease(start, stop, num, function) -> numpy.array:
    """see https://easings.net/ for functions"""
    distance = stop - start
    ease = numpy.array(list(map(function, numpy.linspace(0, 1, num))))
    output = start + ease * distance
    return output


def ease_in(start, stop, num, power=3) -> numpy.array:
    return ease(start, stop, num, function=lambda x: x**power)


def ease_out(start, stop, num, power=3) -> numpy.array:
    return ease(start, stop, num, function=lambda x: 1 - (1 - x) ** power)


def ease_in_out(start, stop, num, power=3) -> numpy.array:
    def _in_out(x, power):
        return 4 * x**power if x < 0.5 else 1 - (-2 * x + 2) ** power / 2

    return ease(start, stop, num, function=lambda x: _in_out(x, power))


def damping_response(t):
    baseline = 1
    amp = -0.2
    damping = 0.4
    phase = 0
    freq = 0.9
    decay = damping * freq
    return baseline + amp * numpy.e ** (-decay * t) * numpy.cos(freq * t - phase)
