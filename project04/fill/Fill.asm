// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@8191
D = A
@stop
M = D

(LOOP)
@i
M = 0
@KBD
D = M
@BLACK
D;JGT
@WHITE
0;JMP

(WHITE)
@i
D = M
@SCREEN
A = D + A
M = 0
@i
M = M + 1
D = M
@stop
D = D - M
@LOOP
D;JGT
@WHITE
0;JMP

(BLACK)
@i
D = M
@SCREEN
A = D + A
M = -1
@i
M = M + 1
D = M
@stop
D = D - M
@LOOP
D;JGT
@BLACK
0;JMP
