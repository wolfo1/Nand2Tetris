"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from Parser import Parser

# common code for all push types
PUSH_CMD = "@SP\nA=M\nM=D\n@SP\nM=M+1\n"
# common code for several pop types
POP_CMD = "@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n"
INIT_CMD = "@256\nD=A\n@SP\nM=D\n"


def write_pop_static(index: int, file_name: str) -> str:
    return f"@SP\nM=M-1\nA=M\nD=M\n@{file_name}.{index}\nM=D\n"


def write_pop_temp_pointer(seg: str, index: int) -> str:
    c_cmd = {"temp": f"@{(5 + index)}\n", "pointer": f"@{3 + index}\n"}
    return f"{c_cmd[seg]}D=A\n" + POP_CMD


def write_pop_this_that_arg_lcl(seg: str, index: int) -> str:
    c_cmd = {"this": "@THIS\n", "that": "@THAT\n", "argument": "@ARG\n", "local": "@LCL\n"}
    return f"@{index}\nD=A\n{c_cmd[seg]}D=D+M\n" + POP_CMD


def write_push_static_temp_pointer(seg: str, index: int, file_name: str) -> str:
    c_cmd = {"static": f"{file_name}.{index}\n", "temp": f"{(5 + index)}\n",
             "pointer": f"{(3 + index)}\n"}
    return f"@{c_cmd[seg]}D=M\n" + PUSH_CMD


def write_push_this_that_arg_lcl(seg: str, index: int) -> str:
    c_cmd = {"this": "@THIS\n", "that": "@THAT\n", "argument": "@ARG\n", "local": "@LCL\n"}
    return f"@{index}\nD=A\n{c_cmd[seg]}A=D+M\nD=M\n" + PUSH_CMD


def write_push_constant(index: int) -> str:
    return f"@{index}\nD=A\n" + PUSH_CMD


def write_add_sub(cmd: str) -> str:
    # dictionary of the add or sub c commands.
    c_cmd = {"add": "M=D+M\n", "sub": "M=M-D\n"}
    # format string for either add or sub
    return f"@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\n{c_cmd[cmd]}@SP\nM=M+1\n"


def write_neg_not_sleft_sright(cmd: str) -> str:
    c_cmd = {"neg": "M=-M\n", "not": "M=!M\n", "shiftleft": "M=M<<\n", "shiftright": "M=M>>\n"}
    return f"@SP\nA=M-1\n{c_cmd[cmd]}"


def write_and_or(cmd: str) -> str:
    c_cmd = {"and": "M=D&M\n", "or": "M=D|M\n"}
    return f"@SP\nM=M-1\nA=M\nD=M\n@SP\nA=M-1\n{c_cmd[cmd]}"


def write_eq_gt_lt(cmd: str, label: str) -> str:
    # lt -> x < y is true, x >= y is false
    c_cmd = {"eq": "JEQ\n", "gt": "JGT\n", "lt": "JLT\n"}
    asm_code = ""
    if cmd != "eq":
        # check if y is negative or positive
        asm_code += f"@SP\nA=M-1\nD=M\n@negy{label}\nD;JLT\n@posy{label}\nD;JGE\n"
        # if y is negative, check if x >=0
        asm_code += f"(negy{label})\n@SP\nA=M-1\nA=A-1\nD=M\n"
        if cmd == "gt":
            asm_code += f"@true{label}\nD;JGE\n"
        elif cmd == "lt":
            asm_code += f"@false{label}\nD;JGE\n"
        # if y >= 0, check if x is negative
        asm_code += f"(posy{label})\n@SP\nA=M-1\nA=A-1\nD=M\n"
        if cmd == "gt":
            asm_code += f"@false{label}\nD;JLT\n"
        elif cmd == "lt":
            asm_code += f"@true{label}\nD;JLT\n"
    # if both signs are the same, check x - y (> / <) 0
    asm_code += f"@SP\nA=M-1\nD=M\nA=A-1\nD=M-D\n@true{label}\nD;{c_cmd[cmd]}"
    # result is false
    asm_code += f"(false{label})\n@SP\nM=M-1\nA=M-1\nM=0\n@cont{label}\n0;JMP\n"
    # result is true
    asm_code += f"(true{label})\n@SP\nM=M-1\nA=M-1\nM=-1\n(cont{label})\n"
    return asm_code


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.file_name = ""
        # will be used to create new labels for static args.
        self.nextLabel = 0
        self.nextCallLabel = 0

    def set_file_name(self, filename: str) -> None:
        """
        Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # begin by writing a comment with the exact command
        asm_code = "// " + command + "\n"
        # call each writing function specific to a group of commands that uses similar code
        if command in ["add", "sub"]:
            asm_code += write_add_sub(command)
        elif command in ["neg", "not", "shiftleft", "shiftright"]:
            asm_code += write_neg_not_sleft_sright(command)
        elif command in ["and", "or"]:
            asm_code += write_and_or(command)
        elif command in ["eq", "gt", "lt"]:
            label = "." + self.file_name + "." + str(self.nextLabel)
            self.nextLabel += 1
            asm_code += write_eq_gt_lt(command, label)
        # write the final code into the output file
        print(asm_code, file=self.output_stream)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # first write a comment with the command type
        asm_code = f"// {command} {segment} {index}\n"
        # call each writing function specific to a group of commands that uses similar code
        # push command
        if command == Parser.C_PUSH:
            if segment == "constant":
                asm_code += write_push_constant(index)
            elif segment in ["static", "temp", "pointer"]:
                asm_code += write_push_static_temp_pointer(segment, index, self.file_name)
            elif segment in ["this", "that", "argument", "local"]:
                asm_code += write_push_this_that_arg_lcl(segment, index)
        # pop command
        elif command == Parser.C_POP:
            if segment == "static":
                asm_code += write_pop_static(index, self.file_name)
            elif segment in ["this", "that", "argument", "local"]:
                asm_code += write_pop_this_that_arg_lcl(segment, index)
            elif segment in ["temp", "pointer"]:
                asm_code += write_pop_temp_pointer(segment, index)
        # write the final code into the output file
        print(asm_code, file=self.output_stream)

    def writeBranching(self, command: str, label: str):
        # write a comment with command information.
        print(f"// {command} {label}", file=self.output_stream)
        label = self.file_name + "." + label
        if command == Parser.C_LABEL:
            self.writeLabel(label)
        elif command == Parser.C_IFGOTO:
            self.writeIf(label)
        elif command == Parser.C_GOTO:
            self.writeGoto(label)

    def writeInit(self) -> None:
        print(INIT_CMD, file=self.output_stream)
        self.writeCall("Sys.init", 0)

    def writeLabel(self, label: str) -> None:
        print(f"({label})\n", file=self.output_stream)

    def writeGoto(self, label: str) -> None:
        print(f"@{label}\n0;JMP\n", file=self.output_stream)

    def writeIf(self, label: str) -> None:
        print(f"@SP\nM=M-1\nA=M\nD=M\n@{label}\nD;JNE\n", file=self.output_stream)

    def writeFunction(self, name: str, var: int) -> None:
        print(f"// {name} function initialize {var} arguments", file=self.output_stream)
        endLabel = name + "$Start"
        initLabel = name + "$Args"
        self.writeLabel(name)
        print("// put num of arguemnts into @R13", file=self.output_stream)
        print(f"@{var}\nD=A\n", file=self.output_stream)
        print(f"@{endLabel}\nD;JEQ\n", file=self.output_stream)
        self.writeLabel(initLabel)
        print("@SP\nA=M\nM=0\n@SP\nM=M+1\n", file=self.output_stream)
        print(f"D=D-1\n@{initLabel}\nD;JGT\n", file=self.output_stream)
        self.writeLabel(endLabel)

    def writeReturn(self) -> None:
        asm_code = "// Return\n"
        asm_code += "// put LCL (endframe) into @R14\n"
        asm_code += "@LCL\nD=M\n@R14\nM=D\n"
        asm_code += "// ret_address = *(endframe - 5) into @R15\n"
        asm_code += "@5\nD=A\n@R14\nA=M-D\nD=M\n@R15\nM=D\n"
        asm_code += "// SP = ARG + 1\n"
        asm_code += "@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M+1\n@SP\nM=D\n"
        asm_code += "// THAT,THIS,ARG,LCL = *(endframe - i)\n"
        asm_code += "@R14\nAM=M-1\nD=M\n@THAT\nM=D\n"
        asm_code += "@R14\nAM=M-1\nD=M\n@THIS\nM=D\n"
        asm_code += "@R14\nAM=M-1\nD=M\n@ARG\nM=D\n"
        asm_code += "@R14\nAM=M-1\nD=M\n@LCL\nM=D\n"
        asm_code += "@R15\nA=M\n0;JMP\n"
        print(asm_code, file=self.output_stream)

    def writeCall(self, name: str, num: int) -> None:
        returnLabel = name + "$ret." + str(self.nextCallLabel)
        self.nextCallLabel += 1
        asm_code = f"// CALL {name} {num}\n"
        asm_code += "// return address to SP\n"
        asm_code += f"@{returnLabel}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        asm_code += "// push LCL, ARG, THIS, THAT\n"
        asm_code += "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        asm_code += "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        asm_code += "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        asm_code += "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        asm_code += "// ARG = SP-5-numArgs\n"
        asm_code += f"@SP\nD=M\n@5\nD=D-A\n@{num}\nD=D-A\n@ARG\nM=D\n"
        asm_code += "// LCL = SP\n"
        asm_code += "@SP\nD=M\n@LCL\nM=D\n"
        asm_code += f"// GOTO {name}\n"
        asm_code += f"@{name}\n0;JMP\n"
        print(asm_code, file=self.output_stream)
        self.writeLabel(returnLabel)
