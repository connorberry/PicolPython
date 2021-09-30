# Python implementation of Picol (small Tcl interpreter)

# *** Enums ***
PICOL_OK       = 0
PICOL_ERR      = 1
PICOL_RETURN   = 2
PICOL_BREAK    = 3
PICOL_CONTINUE = 4

PT_ESC = 7
PT_STR = 8
PT_CMD = 9
PT_VAR = 10
PT_SEP = 11
PT_EOL = 12
PT_EOF = 13


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
    level = 3
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
                p.p -= 1
                p.end = p.p
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
        error_message = "Command '%s' already defined".format(name)
        picolSetResult(i, error_message)
    c = PicolCmd()
    c.name = name
    c.func = f
    c.privdata = privdata
    c.next = i.commands
    i.commands = c
    return PICOL_OK











