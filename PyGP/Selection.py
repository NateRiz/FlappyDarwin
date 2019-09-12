from random import choice
from PyGP.Hardware import Hardware

def tournament(hws):
    next_gen = []
    while len(next_gen) < len(hws):
        a = choice(hws)
        b = choice(hws)
        if a.fitness >= b.fitness:
            next_gen.append(copy(a))
        else:
            next_gen.append(copy(b))
    return next_gen

def elite(hws, k):
    next_gen = []
    inst_lib = hws[0].inst_lib
    hws.sort(key=lambda hw: hw.fitness, reverse=True)
    [next_gen.append(copy(hw)) for hw in hws[:k]]
    while len(next_gen) < len(hws):
        hw = Hardware(inst_lib)
        hw.generate_program()
        next_gen.append(hw)
    return next_gen

def copy(src: Hardware):
    hw = Hardware(src.inst_lib)

    for i in src.instructions:
        inst = src.inst_lib.lib[i.name]
        hw.instructions.append(inst[0](*inst[1:]))
        hw.instructions[-1].args = list(i.args)

    return hw
