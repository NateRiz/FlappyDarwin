from random import choice
from PyGP.Hardware import Hardware


def tournament(hws):
    next_gen = []
    while len(next_gen) < len(hws):
        a = choice(hws)
        b = choice(hws)
        if a.fitness >= b.fitness:
            next_gen.append(a.copy())
        else:
            next_gen.append(b.copy())

    for i, hw in enumerate(next_gen):
        hw.traits = i

    return next_gen


def elite(hws, k):
    next_gen = []
    inst_lib = hws[0].inst_lib
    hws.sort(key=lambda hw: hw.fitness, reverse=True)
    [next_gen.append(hw.copy()) for hw in hws[:k]]

    while len(next_gen) < len(hws):
        hw = Hardware(inst_lib)
        hw.generate_program()
        next_gen.append(hw)

    for i, hw in enumerate(next_gen):
        hw.traits = i

    return next_gen
