@i
M = 1
D = M
// edge case: R15 <= 1, exit right away
@R15
D = M - 1
@EXIT
D;JLE
// INSERTION SORT
(OUTERLOOP)
// Outer loop condition: i < R15
@i
D = M
@R15
D = D - M
@EXIT
D;JGE
// j = i
@i
D = M
@j
M = D

(INNERLOOP)
// store A[j] address to @aj, & A[j-1] address to @aj2
@j
D = M
@R14
A = D + M
D = A
@aj
M = D
@aj2
M = D - 1
// Inner loop condition 1: j > 0
@j
D = M
@ENDINLOOP
D;JLE
// Inner loop condition 2: A[j-1] < A[j]
@aj
A = M
D = M
@aj2
A = M
D = D - M
@ENDINLOOP
D;JLE

// SWAP
@aj
A = M
D = M
@temp // copy A[j] to temp address
M = D
@aj2
A = M
D = M
@aj // swap A[j] = A[j-1]
A = M
M = D
@temp
D = M
@aj2 // swap A[j-1] = A[j]
A = M
M = D
// j = j - 1
@j
M = M - 1
@INNERLOOP
0;JMP

(ENDINLOOP)
// i = i + 1
@i
M = M + 1
@OUTERLOOP
0;JMP

(EXIT)
@EXIT
0;JMP