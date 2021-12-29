"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer

INDENT = "  "
OP = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
UANRY_OP = ["~", "-", "^", "#"]
CLASS_VAR_DEC = ["static", "field"]
CLASS_SUBROUTINE = ["function", "method", "constructor"]


def write_open(tag):
    return f"<{tag}>\n"


def write_close(tag):
    return f"</{tag}>\n"


def write_tag(tag, word):
    return f"<{tag}> {word} </{tag}>\n"


class CompilationEngine:
    def __init__(self, input_stream, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = JackTokenizer(input_stream)
        self.output = output_stream
        self.depth = 0
        self.counter = 0
        self.compiled_text = ""

    def write_indent(self):
        return "    " * self.depth

    def writeCurrToken(self):
        tokenName = self.tokenizer.get_name()
        tokenType = self.tokenizer.token_type().lower()
        if tokenType == "string_const":
            tokenType = "stringConstant"
        elif tokenType == "int_const":
            tokenType = "integerConstant"
        if tokenName == ">":
            tokenName = "&gt;"
        if tokenName == "<":
            tokenName = "&lt;"
        if tokenName == "\"":
            tokenName = "&quot;"
        if tokenName == "&":
            tokenName = "&amp;"
        self.compiled_text += self.write_indent() + write_tag(tokenType, tokenName)

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.compiled_text += write_open("class")
        self.depth = 1
        # write keyword class and "{" symbol.
        for i in range(3):
            self.tokenizer.advance()
            self.writeCurrToken()
        self.tokenizer.advance()
        # write all class var decs (if any)
        while self.tokenizer.get_name() in CLASS_VAR_DEC:
            self.compile_class_var_dec()
        # write all class subroutines (if any)
        while self.tokenizer.get_name() in CLASS_SUBROUTINE:
            self.counter += 1
            self.compile_subroutine()
        # close class
        self.writeCurrToken()
        self.depth -= 1
        self.compiled_text += "</class>"
        print(self.compiled_text, file=self.output)

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.compiled_text += self.write_indent() + write_open("classVarDec")
        self.depth += 1
        while self.tokenizer.get_name() != ";":
            self.writeCurrToken()
            self.tokenizer.advance()
        # write ";"
        self.writeCurrToken()
        self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("classVarDec")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        self.compiled_text += self.write_indent() + write_open("subroutineDec")
        self.depth += 1
        # write i.e "{func_type} {return_type} {func_name}("
        for i in range(4):
            self.writeCurrToken()
            self.tokenizer.advance()
        # write parameter list
        self.compile_parameter_list()
        self.writeCurrToken()
        # open <subroutineBody>
        self.compiled_text += self.write_indent() + write_open("subroutineBody")
        self.depth += 1
        # write "{"
        self.tokenizer.advance()
        self.writeCurrToken()
        # check for VAR DECs
        self.tokenizer.advance()
        while self.tokenizer.get_name() == "var":
            self.compile_var_dec()
        # compile statments
        self.compile_statements()
        # compile "}" and close tags
        self.writeCurrToken()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("subroutineBody")
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("subroutineDec")
        self.tokenizer.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.compiled_text += self.write_indent() + write_open("parameterList")
        self.depth += 1
        name = self.tokenizer.get_name()
        while name != ")":
            self.writeCurrToken()
            self.tokenizer.advance()
            name = self.tokenizer.get_name()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.compiled_text += self.write_indent() + write_open("varDec")
        self.depth += 1
        name = self.tokenizer.get_name()
        while name != ";":
            self.writeCurrToken()
            self.tokenizer.advance()
            name = self.tokenizer.get_name()
        # write ";"
        self.writeCurrToken()
        self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.compiled_text += self.write_indent() + write_open("statements")
        self.depth += 1
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
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.compiled_text += self.write_indent() + write_open("doStatement")
        self.depth += 1
        # write subroutine call: "do {subroutineCall}"
        self.compile_subroutine_call()
        # write ";"
        self.writeCurrToken()
        self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("doStatement")

    def compile_subroutine_call(self) -> None:
        name = self.tokenizer.get_name()
        while name != "(":
            self.writeCurrToken()
            self.tokenizer.advance()
            name = self.tokenizer.get_name()
        # write "("
        self.writeCurrToken()
        self.tokenizer.advance()
        self.compile_expression_list()
        # write ")"
        self.writeCurrToken()
        self.tokenizer.advance()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.compiled_text += self.write_indent() + write_open("letStatement")
        self.depth += 1
        # write "let {varname}"
        for i in range(2):
            self.writeCurrToken()
            self.tokenizer.advance()
        if self.tokenizer.get_name() == "[":
            # write "["
            self.writeCurrToken()
            self.tokenizer.advance()
            # write expression
            self.compile_expression()
            # write "]"
            self.writeCurrToken()
            self.tokenizer.advance()
        # write "="
        self.writeCurrToken()
        self.tokenizer.advance()
        # write expression
        self.compile_expression()
        # write ";"
        self.writeCurrToken()
        self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.compiled_text += self.write_indent() + write_open("whileStatement")
        self.depth += 1
        for i in range(2):
            self.writeCurrToken()
            self.tokenizer.advance()
        self.compile_expression()
        for i in range(2):
            self.writeCurrToken()
            self.tokenizer.advance()
        self.compile_statements()
        self.writeCurrToken()
        self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.compiled_text += self.write_indent() + write_open("returnStatement")
        self.depth += 1
        self.writeCurrToken()
        self.tokenizer.advance()
        if self.tokenizer.get_name() != ";":
            self.compile_expression()
        self.writeCurrToken()
        self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.compiled_text += self.write_indent() + write_open("ifStatement")
        self.depth += 1
        for i in range(2):
            self.writeCurrToken()
            self.tokenizer.advance()
        self.compile_expression()
        for i in range(2):
            self.writeCurrToken()
            self.tokenizer.advance()
        self.compile_statements()
        self.writeCurrToken()
        self.tokenizer.advance()
        if self.tokenizer.get_name() == "else":
            for i in range(2):
                self.writeCurrToken()
                self.tokenizer.advance()
            self.compile_statements()
            self.writeCurrToken()
            self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compiled_text += self.write_indent() + write_open("expression")
        self.depth += 1
        self.compile_term()
        while self.tokenizer.get_name() in OP:
            self.writeCurrToken()
            self.tokenizer.advance()
            self.compile_term()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("expression")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.compiled_text += self.write_indent() + write_open("term")
        self.depth += 1
        nextToken = self.tokenizer.tokens[self.tokenizer.currToken + 1]
        # array var: x[5]
        if nextToken == "[":
            for i in range(2):
                self.writeCurrToken()
                self.tokenizer.advance()
            self.compile_expression()
            # write "]"
            self.writeCurrToken()
            self.tokenizer.advance()
        # (expression), i.e: (i + 2).
        elif self.tokenizer.get_name() == "(":
            # write "("
            self.writeCurrToken()
            self.tokenizer.advance()
            # write expression inside brackets
            self.compile_expression()
            # write ")"
            self.writeCurrToken()
            self.tokenizer.advance()
        elif self.tokenizer.get_name() in UANRY_OP:
            self.writeCurrToken()
            self.tokenizer.advance()
            self.compile_term()
        # subroutine call: {class_name}.{name}({expressionList}) or {name}({expressionList})
        elif nextToken == "(" or nextToken == ".":
            self.compile_subroutine_call()
        else:
            self.writeCurrToken()
            self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.compiled_text += self.write_indent() + write_open("expressionList")
        self.depth += 1
        while self.tokenizer.get_name() != ")":
            self.compile_expression()
            if self.tokenizer.get_name() == ",":
                self.writeCurrToken()
                self.tokenizer.advance()
        self.depth -= 1
        self.compiled_text += self.write_indent() + write_close("expressionList")
