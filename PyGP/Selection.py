from random import choice, shuffle, uniform


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
    hws.sort(key=lambda hw: hw.fitness, reverse=True)
    [next_gen.append(hw.copy()) for hw in hws[:k]]

    while len(next_gen) < len(hws):
        hw = hws[0].copy()
        hw.clear_program()
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


def roulette(hws):
    assert type(hws[0].fitness) == list, F"The hardware fitness should be a list," \
                                      F" even with one element in it. Got {type(hws.fitness)}"
    next_gen = []
    fit_bounds = [hws[0].fitness[0]]
    for i in range(1, len(hws)):
        fit_bounds.append(hws[i].fitness[0]+fit_bounds[-1])

    while len(next_gen) < len(hws):
        x = uniform(0, fit_bounds[-1])
        idx = binary_search(fit_bounds, 0, len(fit_bounds)-1, x)
        next_gen.append(hws[idx].copy())

    return next_gen


def binary_search(arr, l, r, x):
    # based off of
    # https://www.geeksforgeeks.org/binary-search/
    if r >= l:
        mid = l + (r - l) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binary_search(arr, l, mid - 1, x)
        else:
            return binary_search(arr, mid + 1, r, x)
    else:
        return l

