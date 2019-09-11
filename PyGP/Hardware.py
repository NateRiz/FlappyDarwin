from random import randint, choice


class Hardware:
    def __init__(self, inst_lib):
        self.instructions = []  # The actual program : List of Instruction Objects
        self.IP = 0  # Instruction Pointer
        self.EOP = False  # have we reached the end of the program yet?
        self.registers = [0.0] * 24
        self.inst_lib = inst_lib
        self.fitness = -1

        self.MAX_PROGRAM_LENGTH = 128
        self.MIN_PROGRAM_LENGTH = 1

    def reset(self):
        self.IP = 0
        self.EOP = False
        self.registers = [0.0] * 24
        self.fitness = -1

    def tick(self):
        inst_complete = self.instructions[self.IP].run(self)
        if inst_complete:
            self.IP += 1

        self.EOP = self.IP >= len(self.instructions)

    def __len__(self):
        return len(self.instructions) + sum([len(blk) for blk in self.instructions if type(blk) is Block])

    def cache_fitness(self, fitness):
        self.fitness = fitness

    def generate_program(self):
        prog_len = randint(self.MIN_PROGRAM_LENGTH, self.MAX_PROGRAM_LENGTH)
        insts = list(self.inst_lib.lib.values())
        i = 0
        while i < prog_len:
            inst = choice(insts)
            self.instructions.append(inst[0](*inst[1:]))
            self.instructions[-1].args[0] = randint(0, len(self.registers))
            self.instructions[-1].args[1] = randint(0, len(self.registers))
            self.instructions[-1].args[2] = randint(0, len(self.registers))
            if type(self.instructions[-1]) is Block:  # TODO this does not allot for nested loops.
                for _ in range(randint(0, prog_len - i)):
                    inst = choice(insts)
                    self.instructions[-1].instructions.append(inst[0](*inst[1:]))
                    self.instructions[-1].instructions[-1].args[0] = randint(0, len(self.registers))
                    self.instructions[-1].instructions[-1].args[1] = randint(0, len(self.registers))
                    self.instructions[-1].instructions[-1].args[2] = randint(0, len(self.registers))
                    i += 1
            i += 1

    def load_program(self, name):
        with open(name, "r") as file:
            in_block = False
            for line in file:
                if not line.strip(): continue

                if line[0].isalpha():
                    in_block = False

                line = line.split()
                inst_name = line[0]
                il = self.inst_lib.lib[inst_name]
                inst = il[0](*il[1:])
                i = 0
                for arg in line:
                    if arg.isdigit():
                        inst.args[i] = int(arg)
                        i += 1
                        if i >= 3:
                            break
                if in_block:
                    self.instructions[-1].instructions.append(inst)
                else:
                    self.instructions.append(inst)
                if type(inst) is Block:
                    in_block = True

    def __str__(self):
        newline = "\n"
        return F"IP: {self.IP}\n{self.registers}\n{newline.join([str(i) for i in self.instructions])}"


class InstructionLibrary:
    def __init__(self):
        self.lib = {}

    def add_inst(self, name, callback, is_block_type):
        if is_block_type:
            self.lib[name] = (Block, name, callback)
        else:
            self.lib[name] = (Instruction, name, callback)


class InstructionBase:
    def __init__(self, name, callback):
        self.name = name
        self.args = [0, 0, 0]
        self.callback = callback
        self.__repr__ = self.__str__

    def run(self, hardware):
        raise NotImplementedError

    def __str__(self):
        return F"{self.name:<8} {tuple(self.args)}"


class Instruction(InstructionBase):
    def __init__(self, name, callback):
        super().__init__(name, callback)

    def run(self, hardware):
        self.callback(hardware, self.args)
        return True


class Block(InstructionBase):
    def __init__(self, name, callback):
        super().__init__(name, callback)
        self.instructions = []
        self.IP = -1
        self.increment = 0

    def __len__(self):
        return len(self.instructions)

    def __str__(self):
        if self.IP >= 0:
            return str(self.instructions[self.IP])
        return super().__str__()


    def print_full(self):
        return super().__str__() + ("\n\t" if len(self.instructions) else "") + "\n\t".join(
            [str(i) for i in self.instructions])

    def run(self, hardware):
        finished = self.callback(hardware, self.args, self.increment)
        if self.IP == -1 and finished:
            self.IP = -1
            self.increment = 0
            return True

        else:
            if self.IP >= 0:
                self.instructions[self.IP].run(hardware)
            self.IP += 1
            if self.IP >= len(self.instructions):
                self.IP = -1
                self.increment += 1

        return False
