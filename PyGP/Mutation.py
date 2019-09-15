from random import random, choice, randint


def mutate(hw):
    INSERTION_RATE = 0.015
    DELETION_RATE = 0.015
    SWAP_RATE = 0.015
    ARG_RATE = 0.015
    insts = list(hw.inst_lib.lib.values())

    i = 1
    while i < len(hw)+1:

        if len(hw) < hw.MAX_PROGRAM_LENGTH and random() <= INSERTION_RATE:
            inst = choice(insts)
            hw.instructions.insert(i, inst[0](*inst[1:]))
            hw.instructions[i].args[0] = randint(0, len(hw.registers))
            hw.instructions[i].args[1] = randint(0, len(hw.registers))
            hw.instructions[i].args[2] = randint(0, len(hw.registers))

        if random() <= SWAP_RATE:
            del hw.instructions[i-1]
            inst = choice(insts)
            hw.instructions.insert(i, inst[0](*inst[1:]))
            hw.instructions[i-1].args[0] = randint(0, len(hw.registers))
            hw.instructions[i-1].args[1] = randint(0, len(hw.registers))
            hw.instructions[i-1].args[2] = randint(0, len(hw.registers))

        for j in range(3):
            if random() <= ARG_RATE:
                hw.instructions[i-1].args[j] = randint(0, len(hw.registers))

        if len(hw) > hw.MIN_PROGRAM_LENGTH and random() <= DELETION_RATE:
            del hw.instructions[i-1]

        i += 1
