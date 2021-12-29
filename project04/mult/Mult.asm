// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// initilize result to 0 as default case
@R2
M = 0
// if R1 is 0, we can jump directly to the end of the program
@R1
D = M
@END
D;JEQ

// initilize sum to 0
@sum
M = 0
(LOOP)
// add R0 to sum
@R0
D = M
@sum
M = M + D
// check how many times we added R0 to sum, exit from loop if reached R1 times.
@R1
M = M - 1
D = M
@LOOP
D;JGT
// put end result into R2
@sum
D = M
@R2
M = D
(END)
@END
0;JMP