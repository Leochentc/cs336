# CS336 Assignment 1

## Problem unicode1

### (a)
`chr(0)` returns the NUL character (U+0000).

### (b)
Its `repr()` is `'\x00'`, whereas printing it produces no visible character.

### (c)
The NUL character remains part of a Python string,
even though it is invisible when printed.

## Problem unicode2
### (a) why UTF-8？
UTF-8 is generally more space-efficient for English-heavy text because ASCII characters require only one byte, compared with two bytes in UTF-16 and four bytes in UTF-32. It is also widely used on the web, ASCII-compatible, and byte-order independent.
### (b) why Decoder incorrect？
The function incorrectly decodes each byte independently, even though UTF-8 characters can span multiple bytes; for example, b'\xc3\xa9' should decode to é, but the function produces ��.
### (c) sequence that cannot be decoded
b'\xff\xff' is invalid UTF-8 because 0xFF is not a permitted UTF-8 byte, so decoding the sequence raises a UnicodeDecodeError.