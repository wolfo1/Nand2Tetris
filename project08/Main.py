"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


def get_filename(filepath: str) -> str:
    # check for Unix pathing
    if "/" in filepath:
        return filepath.split("/")[-1]
    # check for Windows pathing
    else:
        return filepath.split("\\")[-1]


def translate_file(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    parser = Parser(input_file)
    codewriter = CodeWriter(output_file)
    if bootstrap:
        codewriter.writeInit()
    codewriter.set_file_name(get_filename(filename))
    while parser.has_more_commands():
        parser.advance()
        cmd_type = parser.command_type()
        if cmd_type in Parser.MEMORY_CMDS:
            codewriter.write_push_pop(cmd_type, parser.arg1(), parser.arg2())
        elif cmd_type == Parser.C_MATH:
            codewriter.write_arithmetic(parser.arg1())
        elif cmd_type in Parser.BRANCHING_CMDS:
            codewriter.writeBranching(cmd_type, parser.arg1())
        elif cmd_type == Parser.C_FUNCTION:
            codewriter.writeFunction(parser.arg1(), parser.arg2())
        elif cmd_type == Parser.C_RETURN:
            codewriter.writeReturn()
        elif cmd_type == Parser.C_CALL:
            codewriter.writeCall(parser.arg1(), parser.arg2())


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file)
            bootstrap = False
