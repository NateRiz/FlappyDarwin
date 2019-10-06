from PyGP.Hardware import Hardware, InstructionLibrary
import PyGP.Instructions as inst
import os


def main():
    inst_lib = InstructionLibrary()
    inst_lib.add_inst("Add", inst.add, False)
    inst_lib.add_inst("Sub", inst.sub, False)
    inst_lib.add_inst("Mul", inst.mul, False)
    inst_lib.add_inst("Div", inst.div, False)
    inst_lib.add_inst("Mod", inst.mod, False)
    inst_lib.add_inst("Eq", inst.eq, False)
    inst_lib.add_inst("Greater", inst.greater, False)
    inst_lib.add_inst("Less", inst.less, False)
    inst_lib.add_inst("Not", inst.not_, False)
    inst_lib.add_inst("Assign", inst.assign, False)
    inst_lib.add_inst("Copy", inst.copy, False)
    inst_lib.add_inst("While", inst.while_, True)
    inst_lib.add_inst("Close", inst.close, False)
    inst_lib.add_inst("Break", inst.break_, False)
    inst_lib.add_inst("For", inst.for_, True)
    inst_lib.add_inst("If", inst.if_, True)

    hw = Hardware(inst_lib)
    s=[0]*24
    s[0]=5
    s[1]=25
    test(hw, "For", s)

    s=[0]*24
    s[1]=1
    s[2]=15
    test(hw, "While", s)

    s=[0]*24
    s[2]=2
    s[3]=1
    s[4]=16
    test(hw, "If", s)

def test(hw, file, solution):
    cwd = os.getcwd()
    path = os.path.join(cwd, "UnitTest", file)

    try:
        hw.clear_program()
        hw.load_program(path)

        while not hw.EOP:
            hw.tick()
        assert hw.registers == solution
        print(F"Test: [{file}] Passed\n"+"_"*30)

    except Exception as e:
        print("Error:", str(e))
        print(F"Expected: {[str(i)+': '+str(v) for i, v in enumerate(solution) if v]}")
        print(F"Got     : {[str(i)+': '+str(v) for i, v in enumerate(hw.registers) if v]}")



if __name__ == '__main__':
    main()