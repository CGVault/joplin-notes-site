
## How does a computer program work?

A computer can perform simple calculations super fast in order to solve complex problems, but requires someone to program its abilities. As it cannot use itself, just like an instrument can't play itself without a musician, one must create instructions (a program) in a language (programming language) the computer can understand.

## Natural languages vs. programming languages

Natural languages - develop new words and remove old ones as needed over time, ever evolving. Languages we use daily like English, French, etc.

Machine languages -  created by people to interact with computers. Computers use "machine language" to understand instructions. Machine code/language is in binary while just above that is Assembly.

Instruction list - list of known commands (IL).

## What makes a language?

Alphabet - set of symbols used to build words (IL is the alphabet of machine language).

Lexis - set of words offered by the language.

Syntax - rules to ensure a string of words is a valid sentence.

Semantics - set of rules to ensure a strong of words makes sense.

Low level programming languages - code written closer to machine language, difficult to understand for people.

High level programming languages - code closer to natural languages (like English), easier for people to understand.

Source code - instructions written in a high level programming language.

Source file - file containing the source code

## Compilation vs. interpretation

Compilation - high level programming language is translated into machine code once using a compiler, resulting in an executable file. Changing your program requires you to recompile a new executable file.

Interpretation - high level programming language is translated every time it runs by an interpreter. You cannot distribute your program easily, as the other person needs the interpreter to run it too.

Almost all high level languages are designed to either be compiled, or interpreted. Very rarely is a language designed to do both.

## What does the interpreter actually do?

Code is stored as text on your compute.

The interpreter checks if the code is correct (ensures all four parts of the language is followed)

If an error is detected, the interpreter stops and throughs out an error code.

If an error is detected, the error code refers to where there error was found not where it started. For example using a variable which wasn't declared, the error code would be where the variable was used not where it was meant to be declared.

If the line of code is correct, it will be executed. This read-check-execute cycle occurs over and over again while the interpreter is running your code.

## Compilation vs. interpretation

|     | Compilation | Interpretation |
| --- | --- | --- |
| Pros | Execution of the code is faster  <br><br/>Only the user requires the compiler  <br><br/>The translated code is in machine language, so its hard for others to reverse engineer it | You can the code as soon as you finish writing it, no extra translation steps taking time  <br><br/>Code is stored using the programming language not machine language, so you can run it on other computers using a different machine language and architecture (x86 vs ARM systems |
| Cons | The compilation itself can be time consuming and you cannot run your code while this is happening  <br><br/>You need a compiler for each hardware platform you want your code to run on (a compiler for PC, and Xbox for gaming for example) | Interpretation won't be as fast as you think because the interpreter shares system resources with the rest of the computer while your code is running  <br><br/>Both you and the end user must have the interpreter to run your code |

In regards to Python, its designed as a interpreted language, hence you need a python interpreter to use it.

Interpreted languages are known as scripting languages, and their source code is often referred to as scripts.

## What is Python and who created it?

Python is a high level programming language used for general purpose coding created by Guido van Rossum and was named after Monty Python's Flying Circus a old tv series.

## Python goals

Python was made to be easy and intuitive to use, it is open source so anyone and contribute to its libraries, the code is understandable in plain English and it was created for everyday tasks to allow for shorter development time.

## What makes Python special?

Python is easy to learn, teach, use, understand and obtain. However, its downsides are that it isn't the fastest programming language for performance and although making mistakes is harder due to its simplicity, the errors appear in odd spots so simple debugging techniques are not as effective.

## Python rivals?

Perl - a scripting language created by Larry Wall, and is more traditional closer to the C programming languages

Ruby - a scripting language created by Yukihiro Matsumoto, and is more innovative than python with newer methods and tools.

Python lives in between these two options.

## Where can we see Python in action?

Python is used in many areas from web applications, security tools for penetration testers, to applications used by scientists.

## Why not Python?

Due to performance being slower than the bare metal low level programming languages, you wouldn't use Python to create drivers for hardware, graphical engines to render objects and video game engines such as Unreal Engine. Python is also not used for mobile applications, at least for now this could someday happen.

## There is more than one Python

Python 2 is the original development branch of python that has since been disconinued, the programming language itself is still used sometimes in older programs and it does recieve security updates. Python 3 is the current development branch of python, the language changes between updates. These two are technically different languages all together as the syntax, some keywords, etc are different.

## Python aka CPython

CPython is the canonical (main original) python langauge maintained by the creator on the python community in the python software foundation. Although Python was written in the C programming language which is efficient, python itself isnt very fast. Cython is a python version used to create performance sensitive scripts, and they are automatically translated into C when the script is used, used for complex mathematics for example.

## Jython

Jython is python written using Java instead of C. Mainly used to add python capabilities to systems originally written in java. This is written using Python 2 standards, no Python 3 standard Jython has been created yet.

## PyPy and RPython

PyPy is python written in a python like environment, RPython is an example of this, known as restricted python. PyPy is not ran as python, it translates into the C programming language before being executed. This version of python is more so to help devlop the python programming language itself rather than used for building scripts and applications.

&nbsp;