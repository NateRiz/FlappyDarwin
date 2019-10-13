from random import random, choice, randint


def mutate(hw):
    INSERTION_RATE = 0.005
    DELETION_RATE = 0.005
    SWAP_RATE = 0.005
    ARG_RATE = 0.001
    insts = list(hw.inst_lib.lib.values())

    i = 1
    while i < len(hw)+1:

        if len(hw) < hw.MAX_PROGRAM_LENGTH and random() <= INSERTION_RATE:
            inst = choice(insts)
            hw.instructions.insert(i, inst[0](*inst[1:]))
            hw.instructions[i].args[0] = randint(0, len(hw.registers)-1)
            hw.instructions[i].args[1] = randint(0, len(hw.registers)-1)
            hw.instructions[i].args[2] = randint(0, len(hw.registers)-1)

        if random() <= SWAP_RATE:
            del hw.instructions[i-1]
            inst = choice(insts)
            hw.instructions.insert(i-1, inst[0](*inst[1:]))
            hw.instructions[i-1].args[0] = randint(0, len(hw.registers)-1)
            hw.instructions[i-1].args[1] = randint(0, len(hw.registers)-1)
            hw.instructions[i-1].args[2] = randint(0, len(hw.registers)-1)

        for j in range(3):
            if random() <= ARG_RATE:
                hw.instructions[i-1].args[j] = randint(0, len(hw.registers)-1)

        if len(hw) > hw.MIN_PROGRAM_LENGTH and random() <= DELETION_RATE:
            del hw.instructions[i-1]

        i += 1

def recombination(hws):
    RATE = .02
    for hw1 in hws:
        if random() <= RATE:
            hw2 = choice(hws)
            while hw2 == hw1:
                hw2 = choice(hws)

            hw1_inst_len = len(hw1.instructions)//2

            for i in range(len(hw2.instructions)//2):
                inst = hw1.inst_lib.get_inst(hw2.instructions[i].name)
                inst.args = list(hw2.instructions[i].args)
                hw1.instructions.append(inst)

            del hw2.instructions[:len(hw2.instructions)//2]

            for i in range(hw1_inst_len):
                inst = hw2.inst_lib.get_inst(hw1.instructions[i].name)
                inst.args = list(hw1.instructions[i].args)
                hw2.instructions.append(inst)

            del hw1.instructions[:hw1_inst_len]

            hw1.cache_dirty = True
            hw2.cache_dirty = True




