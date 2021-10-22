### This file is obsolete - look at new_picol.py for the a complete (working) example
### This file has subtle errors during runtime.

# Python implementation of Picol (small Tcl interpreter)

# *** Enums ***
import sys

PICOL_OK       = 0
PICOL_ERR      = 1
PICOL_RETURN   = 2
PICOL_BREAK    = 3
PICOL_CONTINUE = 4

PT_ESC = 5  # was 7
PT_STR = 6  # was 8
PT_CMD = 7  # was 9
PT_VAR = 8  # was 10
PT_SEP = 9  # was 11
PT_EOL = 10  # was 12
PT_EOF = 11  # was 13


class PicolParser:
    # def __init__(self, text, p, len, start, end, type, insidequote):
    #     self.text = text
    #     self.p = p
    #     self.len = len
    #     self.start = start
    #     self.end = end
    #     self.type = type
    #     self.insidequote = insidequote
    pass

class PicolVar:
    # def __init__(self, name, val, next):
    #     self.name = name
    #     self.val = val
    #     self.next = next
    pass

# ignoring these (virtual) structures for now
# struct picolInterp /* forward declaration
# typedef int (*picolCmdFunc(struct picolInterp *i, int argc, char **argv, void *privdata)


class PicolCmd:
    # def __init__(self, name, func, privdata, next):
    #     self.name = name
    #     self.func = func
    #     self.privdata = privdata
    #     next = next
    pass

class PicolCallFrame:
    # def __init__(self, vars, parent):
    #     self.vars = vars
    #     self.parent = parent
    pass

class PicolInterp:
    # def __init__(self, level, callframe, commands, result):
    #     self.level = level
    #     self.callframe = callframe
    #     self.commands = commands
    #     self.result = result
    pass

# Adding this to emulate a goto in the original C code
class Err(BaseException):
    pass

def picolInitParser(p, text):
    p.text = text
    p.p = 0
    p.len = len(text)
    p.start = 0; p.end = 0; p.insidequote = 0
    p.type = PT_EOL


def picolParseSep(p):
    p.start = p.p
    while p.text[p.p] == ' ' or p.text[p.p] == '\t' or p.text[p.p] == '\n' or p.text[p.p] == '\r':
        p.p   += 1
        p.len -= 1
    p.end = p.p - 1
    p.type = PT_SEP
    return PICOL_OK


def picolParseEol(p):
    p.start = p.p
    while p.text[p.p] == ' ' or p.text[p.p] == '\t' or p.text[p.p] == '\n' or p.text[p.p] == '\r' or p.text[p.p] == ';':
        p.p   += 1
        p.len -= 1
    p.end = p.p - 1
    p.type = PT_EOL
    return PICOL_OK


def picolParseCommand(p):
    level = 1
    blevel = 0
    p.p += 1
    p.start = p.p
    p.len -= 1
    while True:
        if p.len == 0:
            break
        elif p.text[p.p] == '[' and blevel == 0:
            level += 1
        elif p.text[p.p] == ']' and blevel == 0:
            level -= 1
            if not level: break
        elif p.text[p.p] == '\\':
            p.p += 1
            p.len -= 1
        elif p.text[p.p] == '{':
            blevel += 1
        elif p.text[p.p] == '}':
            if blevel != 0:
                blevel -= 1
        p.p += 1
        p.len -= 1
    p.end = p.p - 1
    p.type = PT_CMD
    if p.text[p.p] == ']':
        p.p += 1
        p.len -= 1
    return PICOL_OK


def picolParseVar(p):
    # Skip the $
    p.p += 1
    p.start = p.p
    p.len -= 1

    while True:
        if (
                (p.text[p.p] >= 'a' and p.text[p.p] <= 'z') or
                (p.text[p.p] >= '0' and p.text[p.p] <= '9') or
                (p.text[p.p] == '_')
        ):
            p.p += 1
            p.len -= 1
            continue
        break
    if p.start == p.p:  # It's just a single char string "$"
        p.p -= 1
        p.start = p.end = p.p
        p.type = PT_STR
    else:
        p.p -= 1
        p.end = p.p
        p.type = PT_VAR
    return PICOL_OK


def picolParseBrace(p):
    level = 1
    p.p += 1
    p.start = p.p
    p.len -= 1
    while True:
        if p.len >= 2 and p.text[p.p] == '\\':
            p.p += 1
            p.len -= 1
        elif p.len == 0 or p.text[p.p] == '}':
            level -= 1
            if level == 0 or p.len == 0:
                p.end = p.p - 1
                if p.len:
                    p.p += 1
                    p.len -= 1
                p.type = PT_STR
                return PICOL_OK
        elif p.text[p.p] == '{':
            level += 1
        p.p += 1
        p.len -= 1
    return PICOL_OK  # unreached


def picolParseString(p):
    newword = (p.type == PT_SEP or p.type == PT_EOL or p.type == PT_STR)
    if newword and p.text[p.p] == '{':
        return picolParseBrace(p);
    elif newword and p.text[p.p] == '"':
        p.insidequote = 1
        p.p += 1
        p.len -= 1
    p.start = p.p
    while True:
        if p.len == 0:
            p.end = p.p - 1
            p.type = PT_ESC
            return PICOL_OK
        if p.text[p.p] == '\\':
            if p.len >= 2:
                p.p += 1
                p.len -= 1
        elif p.text[p.p] == '$' or p.text[p.p] == '[':
            p.end = p.p - 1
            p.type = PT_ESC
            return PICOL_OK
        elif p.text[p.p] == ' ' or p.text[p.p] == '\n' or p.text[p.p] == '\r' or p.text[p.p] == ';':
            if not p.insidequote:
                p.end = p.p - 1
                p.type = PT_ESC
                return PICOL_OK
        elif p.text[p.p] == '"':
            if p.insidequote:
                p.end = p.p - 1
                p.type = PT_ESC
                p.p += 1
                p.len -= 1
                p.insidequote = 0
                return PICOL_OK
        p.p += 1
        p.len -= 1
    return PICOL_OK  # unreached


def picolParseComment(p):
    while p.len and p.text[p.p] != '\n':
        p.p += 1
        p.len -= 1
    return PICOL_OK


def picolGetToken(p):
    while True:
        if not p.len:
            if p.type != PT_EOL and p.type != PT_EOF:
                p.type = PT_EOL
            else:
                p.type = PT_EOF
            return PICOL_OK
        if p.text[p.p] == ' ' or p.text[p.p] == '\t' or p.text[p.p] == '\r':
            if p.insidequote:
                return picolParseString(p)
            return picolParseSep(p)
        elif p.text[p.p] == '\n' or p.text[p.p] == ';':
            if p.insidequote:
                return picolParseString(p)
            return picolParseEol(p)
        elif p.text[p.p] == '[':
            return picolParseCommand(p)
        elif p.text[p.p] == '$':
            return picolParseVar(p)
        elif p.text[p.p] == '#':
            if p.type == PT_EOL:
                picolParseComment(p)
                continue
            return picolParseString(p)
        else:    # default
            return picolParseString(p)
    return PICOL_OK  # unreached


def picolInitInterp(i):
    i.level = 0
    i.callframe = PicolCallFrame()
    i.callframe.vars = None
    i.callframe.parent = None
    i.commands = None
    i.result = ""


def picolSetResult(i, s):
    i.result = s


def picolGetVar(i, name):
    v = i.callframe.vars
    while v:
        if v.name == name:
            return v
        v.next
    return None


def picolSetVar(i, name, val):
    v = picolGetVar(i, name)
    if v:
        v.val = val
    else:
        v = PicolVar()
        v.name = name
        v.val = val
        v.next = i.callframe.vars
        i.callframe.vars = v
    return PICOL_OK


def picolGetCommand(i, name):
    c = i.commands
    while c:
        if c.name == name:
            return c
        c = c.next
    return None


def picolRegisterCommand(i, name, f, privdata):
    c = picolGetCommand(i, name)
    if c:
        error_message = "Command '{}' already defined".format(name)
        picolSetResult(i, error_message)
    c = PicolCmd()
    c.name = name
    c.func = f
    c.privdata = privdata
    c.next = i.commands
    i.commands = c
    return PICOL_OK


# * EVAL *
def picolEval(i, t):
    p = PicolParser()
    argc = 0
    # j is not needed yet
    # errbuf not needed
    argv = [] # Was None
    retcode = PICOL_OK
    picolSetResult(i, "")
    picolInitParser(p, t)
    try:
        while True:
            # t declaration not needed yet
            # tlen delcaration not needed yet
            prevtype = p.type
            picolGetToken(p)
            if p.type == PT_EOF:
                break
            tlen = p.end - p.start + 1
            if tlen < 0: tlen = 0
            t = p.text[p.start:p.start + tlen]
            # don't think I need to do t[tlen] = '\0'
            if p.type == PT_VAR:
                v = picolGetVar(i, t)
                if not v:
                    errormsg = "No such variable '{}'".format(t)
                    # Don't think I need the equivalent of free(t)
                    picolSetResult(i, errormsg)
                    retcode = PICOL_ERR;
                    raise Err
                t = v.val
            elif p.type == PT_CMD:
                retcode = picolEval(i, t)
                if retcode != PICOL_OK: raise Err
                t = i.result
            elif p.type == PT_ESC:
                pass    # !!! escape handling missing */
            elif p.type == PT_SEP:
                prevtype = p.type
                continue

            # We have a complete command + args. Call it!
            if p.type == PT_EOL:
                c = PicolCmd()
                prevtype = p.type
                if argc:
                    c = picolGetCommand(i, argv[0])
                    if not c:
                        errormsg = "No such command '{}'".format(argv[0])
                        picolSetResult(i, errormsg)
                        retcode = PICOL_ERR
                        raise Err
                    retcode = c.func(i, argc, argv, c.privdata)
                    if retcode != PICOL_OK: raise Err
                # Prepare for the next command
                for j in range(0, argc):
                    argv[j] = None
                argv = None
                argc = 0
                continue

            # We have a new token, append to the previous or as new arg?
            if prevtype == PT_SEP or prevtype == PT_EOL:
                # argv = []
                # below was: argv[argc] = t
                argv.append(t)
                argc += 1
            else:  # Interpolation
                oldlen = len(argv[argc-1])
                tlen = len(t)
                # below was: argv[argc - 1] += t
                argv.append(t)

            prevtype = p.type

    except Err:
        return retcode


# * Actual Commands *

def picolArityErr(i, name):
    errormsg = "Wrong number of args for {}".format(name)
    picolSetResult(i, errormsg)
    return PICOL_ERR


def picolCommandMath(i, argc, argv, pd):
    # buf, a, b, c = None, None, None, None
    if argc != 3: return picolArityErr(i, argv[0])
    a = int(argv[1]) ; b = int(argv[2])
    if argv[0][0] == '+': c = a + b
    elif argv[0][0] == '-': c = a - b
    elif argv[0][0] == '*': c = a * b
    elif argv[0][0] == '/': c = a // b
    elif argv[0][0] == '>' and argv[0][1] == '': c = a > b
    elif argv[0][0] == '>' and argv[0][1] == '=': c = a >= b
    elif argv[0][0] == '<' and argv[0][1] == '': c = a < b
    elif argv[0][0] == '<' and argv[0][1] == '=': c = a <= b
    elif argv[0][0] == '=' and argv[0][1] == '=': c = a == b
    elif argv[0][0] == '!' and argv[0][1] == '=': c = a != b
    else: c = 0 # prevent warnings in original code?
    buf = c
    picolSetResult(i, buf)
    return PICOL_OK

def picolCommandPuts(i, argc, argv, pd):
    if argc != 2:
        return picolArityErr(i, argv[0])
    print("{}".format(argv[1]))
    return PICOL_OK


def picolRegisterCoreCommands(i):
    name = ["+", "-", "*", "/", ">", ">=", "<", "<=", "==", "!"]
    for j in name:
        picolRegisterCommand(i, j, picolCommandMath, None)
    picolRegisterCommand(i, "puts", picolCommandPuts, None)


if __name__ == '__main__':
    interp = PicolInterp()
    picolInitInterp(interp)
    picolRegisterCoreCommands(interp)
    while True:
        clibuf = input("picol> ")
        if clibuf == None:
            sys.exit()
        retcode = picolEval(interp, clibuf)
        if interp.result != "":
            print("[{}] {}".format(retcode, interp.result))
    sys.exit()




