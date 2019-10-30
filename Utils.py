from math import sqrt


def clamp(x, min_, max_):
    if x >= max_:
        return max_
    if x <= min_:
        return min_
    return x

def distance(a, b):
    return abs(sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2))
