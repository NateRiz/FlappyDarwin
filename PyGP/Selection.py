from random import choice, shuffle
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
    return next_gen


def lexicase(hws, epsilon=0.05):
    next_gen = []
    while len(next_gen) < len(hws):
        tests = list(range(len(hws[0].fitness)))
        shuffle(tests)

        test_no = 0
        filtered_tests = list(hws)

        while test_no < len(tests) and len(filtered_tests) > 1:
            best = max(filtered_tests, key=lambda hw: hw.fitness[tests[test_no]])
            filtered = [hw for hw in filtered_tests if hw.fitness[tests[test_no]] > best.fitness[tests[test_no]]*1-epsilon]
            if filtered:
                filtered_tests = filtered
            test_no += 1

        next_gen += [f.copy() for f in filtered_tests[:min(len(filtered_tests), len(hws)-len(next_gen))]]

    return next_gen










