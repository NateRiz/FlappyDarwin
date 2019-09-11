from PyGP.Hardware import Block
from random import random, choice, randint


def mutate(inst_container, hw):
    INSERTION_RATE = 0.02
    DELETION_RATE = 0.02
    SWAP_RATE = 0.02
    ARG_RATE = 0.02
    insts = list(hw.inst_lib.lib.values())

    i = 1
    while i < len(inst_container)+1:

        if len(inst_container) < inst_container.MAX_PROGRAM_LENGTH and random() <= INSERTION_RATE:
            inst = choice(insts)
            inst_container.instructions.insert(i, inst[0](*inst[1:]))
            inst_container.instructions[i].args[0] = randint(0, len(inst_container.registers))
            inst_container.instructions[i].args[1] = randint(0, len(inst_container.registers))
            inst_container.instructions[i].args[2] = randint(0, len(inst_container.registers))

        if type(inst_container.instructions[i-1]) is Block:
            mutate(inst_container.instructions[i-1], hw)

        if random() <= SWAP_RATE:
            del inst_container.instructions[i-1]
            inst = choice(insts)
            inst_container.instructions.insert(i, inst[0](*inst[1:]))
            inst_container.instructions[i-1].args[0] = randint(0, len(inst_container.registers))
            inst_container.instructions[i-1].args[1] = randint(0, len(inst_container.registers))
            inst_container.instructions[i-1].args[2] = randint(0, len(inst_container.registers))

        for j in range(3):
            if random() <= ARG_RATE:
                inst_container.instructions[i-1].args[j] = randint(0, len(inst_container.registers))

        if len(inst_container) > inst_container.MIN_PROGRAM_LENGTH and random() <= DELETION_RATE:
            del inst_container.instructions[i-1]

        i += 1
