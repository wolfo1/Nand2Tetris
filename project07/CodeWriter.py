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
    return f"@{index:x}\nD=A\n{c_cmd[seg]}A=D+M\nD=M\n" + PUSH_CMD


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
            label = str(self.nextLabel)
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
