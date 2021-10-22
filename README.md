### Picol Interpreter in Python

This is a straight almost line for line translation of the original C code from Antirez's *Picol* Tcl 
interpreter into Python. It should have essentially the same runtime behavior as the original C code version.

It is missing many things from a full Tcl verion and even from the later more full featured Picol version 
developed by Richard Succhenwirth.

This was mainly a project to understand the original C code as an intermediate step before attempting to 
re-implement it in other languages.

This project currently does not take advantage of any of the possibilities that Python offers to simply 
or shorten the code over the original C code. In particular, the original C code contains a linked list 
implementation that is translated wholesale rather than using the Python native list functionality.