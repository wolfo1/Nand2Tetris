"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

INDENT = "  "
OP = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
UANRY_OP = ["~", "-", "^", "#"]
CLASS_VAR_DEC = ["static", "field"]
CLASS_SUBROUTINE = ["function", "method", "constructor"]


class CompilationEngine:
    def __init__(self, input_stream, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.table = SymbolTable()
        self.writer = VMWriter(output_stream)
        self.tokenizer = JackTokenizer(input_stream)
        self.counter = 0
        self.className = ""
        self.compiled_text = ""
        self.while_index_counter = -1
        self.if_index_counter = -1

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # jump over "class" keyword
        self.tokenizer.advance()
        self.tokenizer.advance()
        # get name of class
        self.className = self.tokenizer.get_name()
        self.tokenizer.advance()
        # jump over "{"
        self.tokenizer.advance()
        # write all class var decs (if any)
        while self.tokenizer.get_name() in CLASS_VAR_DEC:
            self.compile_class_var_dec()
        # write all class subroutines (if any)
        while self.tokenizer.get_name() in CLASS_SUBROUTINE:
            self.counter += 1
            self.compile_subroutine()
        # close class
        self.writer.write()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # add var to symboltable
        kind = self.tokenizer.get_name()
        self.tokenizer.advance()
        varType = self.tokenizer.get_name()
        self.tokenizer.advance()
        name = self.tokenizer.get_name()
        self.tokenizer.advance()
        self.table.define(name, varType, kind)
        # handles the case "var int x, y..."
        while self.tokenizer.get_name() != ";":
            self.tokenizer.advance()
            name = self.tokenizer.get_name()
            self.table.define(name, varType, kind)
            self.tokenizer.advance()
        # advance over ";"
        self.tokenizer.advance()

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # get "{func_type} {return_type} {func_name}("
        self.table.start_subroutine()
        kind = self.tokenizer.get_name()
        self.tokenizer.advance()
        self.tokenizer.advance()  # advance over return type
        funcName = self.tokenizer.get_name()
        functionName = f"{self.className}.{funcName}"
        self.tokenizer.advance()
        if kind == "method":
            self.table.define("this", self.className, "ARG")
        self.tokenizer.advance()  # jump over "("
        # write parameter list
        self.compile_parameter_list()
        self.tokenizer.advance()  # advance over ")"
        self.tokenizer.advance()  # advance over "{"
        # check for VAR DECs
        while self.tokenizer.get_name() == "var":
            self.compile_var_dec()
        numLocals = self.table.var_count('VAR')
        self.writer.write_function(functionName, numLocals)
        if kind == "constructor":
            numOfFields = self.table.var_count('FIELD')
            self.writer.write_push('CONST', numOfFields)
            self.writer.write_call('Memory.alloc', 1)
            self.writer.write_pop('POINTER', 0)
        elif kind == "method":
            self.writer.write_push('ARG', 0)
            self.writer.write_pop('POINTER', 0)
        # compile statments
        self.compile_statements()

        # compile "}" and close tags
        self.tokenizer.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        varType = self.tokenizer.get_name()
        if self.tokenizer.get_name() != ")":
            self.tokenizer.advance()
            name = self.tokenizer.get_name()
            self.tokenizer.advance()
            self.table.define(name, varType, 'ARG')
        while self.tokenizer.get_name() != ")":
            if self.tokenizer.get_name() == ",":
                self.tokenizer.advance()
            varType = self.tokenizer.get_name()
            self.tokenizer.advance()
            name = self.tokenizer.get_name()
            self.tokenizer.advance()
            self.table.define(name, varType, 'ARG')

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.tokenizer.advance()  # skip over the word "var"
        # add var to symbole table

        varType = self.tokenizer.get_name()
        self.tokenizer.advance()
        name = self.tokenizer.get_name()
        self.tokenizer.advance()
        self.table.define(name, varType, 'VAR')
        while self.tokenizer.get_name() != ";":
            if self.tokenizer.get_name() == ",":
                self.tokenizer.advance()
            name = self.tokenizer.get_name()
            self.table.define(name, varType, 'VAR')
            self.tokenizer.advance()
        self.tokenizer.advance()  # advance past ";"

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """

        while self.tokenizer.get_name() != "}":
            name = self.tokenizer.get_name()
            if name == "if":
                self.compile_if()
            elif name == "let":
                self.compile_let()
            elif name == "do":
                self.compile_do()
            elif name == "while":
                self.compile_while()
            elif name == "return":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # write subroutine call: "do {subroutineCall}"
        self.tokenizer.advance()  # do
        self.compile_subroutine_call()
        self.writer.write_pop('TEMP', 0)
        self.tokenizer.advance()  # advances past ";"

    def compile_subroutine_call(self) -> None:
        isObject = False
        isDot = False
        objName = self.tokenizer.get_name()
        # find out if method was called from an object or not. change foo name accordingly.
        if self.table.type_of(objName):
            isObject = True
            subRoutineName = self.table.type_of(objName)
        else:
            subRoutineName = objName
        self.tokenizer.advance()
        # get full subroutine name
        while self.tokenizer.get_name() != "(":
            if self.tokenizer.get_name() == ".":
                isDot = True
            subRoutineName += self.tokenizer.get_name()
            self.tokenizer.advance()
        self.tokenizer.advance()
        # if was called from an object, add object to the expression list.
        if isObject:
            self.tokenizer.tokens.insert(self.tokenizer.currToken, objName)
        elif not isDot:
            subRoutineName = self.className + "." + subRoutineName
            self.tokenizer.tokens.insert(self.tokenizer.currToken, "this")
        n_args = self.compile_expression_list()
        self.tokenizer.advance()  # jump over ")"
        self.writer.write_call(subRoutineName, n_args)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # write "let {varname}"
        self.tokenizer.advance()  # let
        varName = self.tokenizer.get_name()
        self.tokenizer.advance()
        kind = self.table.kind_of(varName)  # need to review this in the end
        if kind == 'VAR':
            kind = 'LOCAL'
        elif kind == 'FIELD':
            kind = 'THIS'
        index = self.table.index_of(varName)
        if self.tokenizer.get_name() == "[":
            self.tokenizer.advance()  # advance past "["
            # write expression
            self.compile_expression()
            self.tokenizer.advance()  # advance past "]"
            self.writer.write_push(kind, index)
            self.writer.write_arithmetic('ADD')
            self.tokenizer.advance()  # advance past "="
            # write expression
            self.compile_expression()
            self.writer.write_pop('TEMP', 0)
            self.tokenizer.advance()  # advance past ";"
            self.writer.write_pop('POINTER', 1)
            self.writer.write_push('TEMP', 0)
            self.writer.write_pop('THAT', 0)
        else:
            self.tokenizer.advance()  # advance past "="
            # write expression
            self.compile_expression()
            self.tokenizer.advance()  # advance past ";"

            self.writer.write_pop(kind, index)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.while_index_counter += 1
        idx = self.while_index_counter
        self.writer.write_label(f"WHILE_EXP{idx}")
        for i in range(2):
            self.tokenizer.advance()  # advance past 'while' and '('
        self.compile_expression()
        self.writer.write_arithmetic('NOT')  # need to check the false condition first
        for i in range(2):
            self.tokenizer.advance()  # advance past ')' and '{'
        self.writer.write_if(f"WHILE_END{idx}")
        self.compile_statements()
        self.writer.write_goto(f"WHILE_EXP{idx}")
        self.writer.write_label(f"WHILE_END{idx}")
        self.tokenizer.advance()  # advance past '}'

    def compile_return(self) -> None:
        """Compiles a return statement."""

        self.tokenizer.advance()
        if self.tokenizer.get_name() != ";":
            self.compile_expression()
        else:
            self.writer.write_push('CONST', 0)

        self.writer.write_return()  # write return
        self.tokenizer.advance()  # advance past ';'

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.if_index_counter += 1
        idx = self.if_index_counter
        for i in range(2):
            self.tokenizer.advance()
        self.compile_expression()
        for i in range(2):
            self.tokenizer.advance()

        self.writer.write_if(f"IF_TRUE{idx}")
        self.writer.write_goto(f"IF_FALSE{idx}")
        self.writer.write_label(f"IF_TRUE{idx}")
        self.compile_statements()
        self.writer.write_goto(f"IF_END{idx}")
        self.tokenizer.advance()  # advance past '{'
        self.writer.write_label(f"IF_FALSE{idx}")
        if self.tokenizer.get_name() == "else":
            for i in range(2):
                self.tokenizer.advance()
            self.compile_statements()
            self.tokenizer.advance()
        self.writer.write_label(f"IF_END{idx}")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.get_name() in OP:
            op = self.tokenizer.get_name()
            self.tokenizer.advance()
            self.compile_term()
            if op == '*':
                self.writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.writer.write_call('Math.divide', 2)
            elif op == '+':
                self.writer.write_arithmetic('ADD')
            elif op == '-':
                self.writer.write_arithmetic('SUB')
            elif op == '&':
                self.writer.write_arithmetic('AND')
            elif op == '|':
                self.writer.write_arithmetic('OR')
            elif op == '<':
                self.writer.write_arithmetic('LT')
            elif op == '>':
                self.writer.write_arithmetic('GT')
            elif op == '=':
                self.writer.write_arithmetic('EQ')

    def compile_term(self) -> None:
        nextToken = self.tokenizer.tokens[self.tokenizer.currToken + 1]
        # array var: x[5]
        if self.tokenizer.get_name() == "(":
            # write "("
            self.tokenizer.advance()
            # write expression inside brackets
            self.compile_expression()
            # write ")"
            self.tokenizer.advance()
        elif self.tokenizer.get_name() in UANRY_OP:
            unary_op = self.tokenizer.get_name()
            self.tokenizer.advance()
            self.compile_term()
            if unary_op == '~':
                self.writer.write_arithmetic('NOT')
            elif unary_op == '-':
                self.writer.write_arithmetic('NEG')
            elif unary_op == '^':
                self.writer.write_arithmetic('shiftright')
            elif unary_op == '#':
                self.writer.write_arithmetic('shiftleft')
        elif self.tokenizer.token_type() == 'INT_CONST':
            name = self.tokenizer.get_name()
            self.tokenizer.advance()
            self.writer.write_push('CONST', name)
        elif self.tokenizer.token_type() == 'STRING_CONST':
            string = self.tokenizer.get_name()
            self.tokenizer.advance()
            self.writer.write_push('CONST', len(string))
            self.writer.write_call('String.new', 1)
            for char in string:
                self.writer.write_push('CONST', ord(char))
                self.writer.write_call('String.appendChar', 2)
        elif self.tokenizer.token_type() == 'KEYWORD':
            keyword = self.tokenizer.get_name()
            self.tokenizer.advance()
            if keyword == 'this':
                self.writer.write_push('POINTER', 0)
            else:
                self.writer.write_push('CONST', 0)
                if keyword == 'true':
                    self.writer.write_arithmetic('NOT')
        elif nextToken == "(" or nextToken == ".":
            self.compile_subroutine_call()
        else:  # first is a var
            if nextToken == "[":
                array_var = self.tokenizer.get_name()  # var name
                self.tokenizer.advance()
                self.tokenizer.advance()  # '['
                self.compile_expression()  # expression
                self.tokenizer.advance()  # ']'
                array_index = self.table.index_of(array_var)
                kind = self.table.kind_of(array_var)
                if kind == 'VAR':
                    kind = 'LOCAL'
                elif kind == 'FIELD':
                    kind = 'THIS'
                self.writer.write_push(kind, array_index)
                self.writer.write_arithmetic('ADD')
                self.writer.write_pop('POINTER', 1)
                self.writer.write_push('THAT', 0)
            else:
                var = self.tokenizer.get_name()
                self.tokenizer.advance()
                kind = self.table.kind_of(var)
                if kind == 'VAR':
                    kind = 'LOCAL'
                elif kind == 'FIELD':
                    kind = 'THIS'
                var_kind = kind
                index = self.table.index_of(var)
                self.writer.write_push(var_kind, index)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        count = 0
        while self.tokenizer.get_name() != ")":
            self.compile_expression()
            count += 1
            if self.tokenizer.get_name() == ",":
                self.tokenizer.advance()
        return count
