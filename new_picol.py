# /* Tcl in ~ 500 lines of code.
#  *
#  * Copyright (c) 2007-2016, Salvatore Sanfilippo <antirez at gmail dot com>
#  * All rights reserved.
#  *
#  * Redistribution and use in source and binary forms, with or without
#  * modification, are permitted provided that the following conditions are met:
#  *
#  *   * Redistributions of source code must retain the above copyright notice,
#  *     this list of conditions and the following disclaimer.
#  *   * Redistributions in binary form must reproduce the above copyright
#  *     notice, this list of conditions and the following disclaimer in the
#  *     documentation and/or other materials provided with the distribution.
#  *
#  * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#  * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  * POSSIBILITY OF SUCH DAMAGE.
#  */
# #include <stdio.h>
# #include <stdlib.h>
# #include <string.h>
#
# enum {PICOL_OK, PICOL_ERR, PICOL_RETURN, PICOL_BREAK, PICOL_CONTINUE};
PICOL_OK = 0
PICOL_ERR = 1
PICOL_RETURN = 2
PICOL_BREAK = 3
PICOL_CONTINUE = 4


# enum {PT_ESC,PT_STR,PT_CMD,PT_VAR,PT_SEP,PT_EOL,PT_EOF};
PT_ESC = 5
PT_STR = 6
PT_CMD = 7
PT_VAR = 8
PT_SEP = 9
PT_EOL = 10
PT_EOF = 11


# struct picolParser {
#     char *text;
#     char *p; /* current text position */
#     int len; /* remaining length */
#     char *start; /* token start */
#     char *end; /* token end */
#     int type; /* token type, PT_... */
#     int insidequote; /* True if inside " " */
# };
class PicolParser:
    pass


# struct picolVar {
#     char *name, *val;
#     struct picolVar *next;
# };
class PicolVar:
    pass

# [Ignore for now]
# struct picolInterp; /* forward declaration */
# typedef int (*picolCmdFunc)(struct picolInterp *i, int argc, char **argv, void *privdata);


# struct picolCmd {
#     char *name;
#     picolCmdFunc func;
#     void *privdata;
#     struct picolCmd *next;
# };
class PicolCmd:
    pass


# struct picolCallFrame {
#     struct picolVar *vars;
#     struct picolCallFrame *parent; /* parent is NULL at top level */
# };
class PicolCallFrame:
    pass


# struct picolInterp {
#     int level; /* Level of nesting */
#     struct picolCallFrame *callframe;
#     struct picolCmd *commands;
#     char *result;
# };
class PicolInterp:
    pass

### Added for Goto emulation
class ArityErr(Exception):
    pass

# void picolInitParser(struct picolParser *p, char *text) {
#     p->text = p->p = text;
#     p->len = strlen(text);
#     p->start = 0; p->end = 0; p->insidequote = 0;
#     p->type = PT_EOL;
# }
def picolInitParser(p, text):
    p.text = text
    p.p = 0
    p.len = len(text)
    p.start = 0
    p.end = 0
    p.insidequote = 0
    p.type = PT_EOL


# int picolParseSep(struct picolParser *p) {
#     p->start = p->p;
#     while(*p->p == ' ' || *p->p == '\t' || *p->p == '\n' || *p->p == '\r') {
#         p->p++; p->len--;
#     }
#     p->end = p->p-1;
#     p->type = PT_SEP;
#     return PICOL_OK;
# }
def picolParseSep(p):
    p.start = p.p
    while p.p < len(p.text) and (p.text[p.p] == ' ' or p.text[p.p] == '\t' or p.text[p.p] == '\n' or p.text[p.p] == '\r'):
        p.p += 1
        p.len -= 1
    p.end = p.p - 1
    p.type = PT_SEP
    return PICOL_OK


# int picolParseEol(struct picolParser *p) {
#     p->start = p->p;
#     while(*p->p == ' ' || *p->p == '\t' || *p->p == '\n' || *p->p == '\r' ||
#           *p->p == ';')
#     {
#         p->p++; p->len--;
#     }
#     p->end = p->p-1;
#     p->type = PT_EOL;
#     return PICOL_OK;
# }
def picolParseEol(p):
    p.start = p.p
    while p.p < len(p.text) and (p.text[p.p] == ' ' or p.text[p.p] == '\t' or p.text[p.p] == '\n' or p.text[p.p] == '\r' or p.text[p.p] == ';'):
        p.p += 1
        p.len -= 1
    p.end = p.p - 1
    p.type = PT_EOL
    return PICOL_OK


# int picolParseCommand(struct picolParser *p) {
#     int level = 1;
#     int blevel = 0;
#     p->start = ++p->p; p->len--;
#     while (1) {
#         if (p->len == 0) {
#             break;
#         } else if (*p->p == '[' && blevel == 0) {
#             level++;
#         } else if (*p->p == ']' && blevel == 0) {
#             if (!--level) break;
#         } else if (*p->p == '\\') {
#             p->p++; p->len--;
#         } else if (*p->p == '{') {
#             blevel++;
#         } else if (*p->p == '}') {
#             if (blevel != 0) blevel--;
#         }
#         p->p++; p->len--;
#     }
#     p->end = p->p-1;
#     p->type = PT_CMD;
#     if (*p->p == ']') {
#         p->p++; p->len--;
#     }
#     return PICOL_OK;
# }
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
            if level == 0: break
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


# int picolParseVar(struct picolParser *p) {
#     p->start = ++p->p; p->len--; /* skip the $ */
#     while(1) {
#         if ((*p->p >= 'a' && *p->p <= 'z') || (*p->p >= 'A' && *p->p <= 'Z') ||
#             (*p->p >= '0' && *p->p <= '9') || *p->p == '_')
#         {
#             p->p++; p->len--; continue;
#         }
#         break;
#     }
#     if (p->start == p->p) { /* It's just a single char string "$" */
#         p->start = p->end = p->p-1;
#         p->type = PT_STR;
#     } else {
#         p->end = p->p-1;
#         p->type = PT_VAR;
#     }
#     return PICOL_OK;
# }
def picolParseVar(p):
    p.p += 1
    p.start = p.p
    p.len -= 1  # Skip the '$'
    while True:
        if p.p < len(p.text) and (
                (p.text[p.p] >= 'a' and p.text[p.p] <= 'z') or
                (p.text[p.p] >= 'A' and p.text[p.p] <= 'Z') or
                (p.text[p.p] >= '0' and p.text[p.p] <= '9') or
                p.text[p.p] == '_'
        ):
            p.p += 1
            p.len -= 1
            continue
        break

    if p.start == p.p:  # It's just a single char string "$"
        p.start = p.end = p.p - 1
        p.type = PT_STR
    else:
        p.end = p.p - 1
        p.type = PT_VAR
    return PICOL_OK


# int picolParseBrace(struct picolParser *p) {
#     int level = 1;
#     p->start = ++p->p; p->len--;
#     while(1) {
#         if (p->len >= 2 && *p->p == '\\') {
#             p->p++; p->len--;
#         } else if (p->len == 0 || *p->p == '}') {
#             level--;
#             if (level == 0 || p->len == 0) {
#                 p->end = p->p-1;
#                 if (p->len) {
#                     p->p++; p->len--; /* Skip final closed brace */
#                 }
#                 p->type = PT_STR;
#                 return PICOL_OK;
#             }
#         } else if (*p->p == '{')
#             level++;
#         p->p++; p->len--;
#     }
#     return PICOL_OK; /* unreached */
# }
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
                if p.len != 0:
                    p.p += 1
                    p.len += 1  # Skip final closing brace
                p.type = PT_STR
                return PICOL_OK

        elif p.text[p.p] == '{':
            level += 1
        p.p += 1
        p.len -= 1

    return PICOL_OK  # (unreached)



# int picolParseString(struct picolParser *p) {
#     int newword = (p->type == PT_SEP || p->type == PT_EOL || p->type == PT_STR);
#     if (newword && *p->p == '{') return picolParseBrace(p);
#     else if (newword && *p->p == '"') {
#         p->insidequote = 1;
#         p->p++; p->len--;
#     }
#     p->start = p->p;
#     while(1) {
#         if (p->len == 0) {
#             p->end = p->p-1;
#             p->type = PT_ESC;
#             return PICOL_OK;
#         }
#         switch(*p->p) {
#         case '\\':
#             if (p->len >= 2) {
#                 p->p++; p->len--;
#             }
#             break;
#         case '$': case '[':
#             p->end = p->p-1;
#             p->type = PT_ESC;
#             return PICOL_OK;
#         case ' ': case '\t': case '\n': case '\r': case ';':
#             if (!p->insidequote) {
#                 p->end = p->p-1;
#                 p->type = PT_ESC;
#                 return PICOL_OK;
#             }
#             break;
#         case '"':
#             if (p->insidequote) {
#                 p->end = p->p-1;
#                 p->type = PT_ESC;
#                 p->p++; p->len--;
#                 p->insidequote = 0;
#                 return PICOL_OK;
#             }
#             break;
#         }
#         p->p++; p->len--;
#     }
#     return PICOL_OK; /* unreached */
# }
def picolParseString(p):
    newword = p.type == PT_SEP or p.type == PT_EOL or p.type == PT_STR
    if newword and p.text[p.p] == '{':
        return picolParseBrace(p)
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

        c = p.text[p.p]
        if c == '\\':
            if p.len >= 2:
                p.p += 1
                p.len -= 1
        elif c == '$' or c == '[':
            p.end = p.p - 1
            p.type = PT_ESC
            return PICOL_OK
        elif c == ' ' or c == '\t' or c == '\n' or c == ';':
            if not p.insidequote:
                p.end = p.p - 1
                p.type = PT_ESC
                return PICOL_OK
        elif c == '"':
            if p.insidequote:
                p.end = p.p - 1
                p.type = PT_ESC
                p.p += 1
                p.len -= 1
                p.insidequote = 0
                return PICOL_OK
        p.p += 1
        p.len -= 1

    return PICOL_OK



# int picolParseComment(struct picolParser *p) {
#     while(p->len && *p->p != '\n') {
#         p->p++; p->len--;
#     }
#     return PICOL_OK;
# }
def picolParseComment(p):
    while p.len and p.text[p.p] != '\n':
        p.p += 1
        p.len -= 1
    return PICOL_OK


# int picolGetToken(struct picolParser *p) {
#     while(1) {
#         if (!p->len) {
#             if (p->type != PT_EOL && p->type != PT_EOF)
#                 p->type = PT_EOL;
#             else
#                 p->type = PT_EOF;
#             return PICOL_OK;
#         }
#         switch(*p->p) {
#         case ' ': case '\t': case '\r':
#             if (p->insidequote) return picolParseString(p);
#             return picolParseSep(p);
#         case '\n': case ';':
#             if (p->insidequote) return picolParseString(p);
#             return picolParseEol(p);
#         case '[':
#             return picolParseCommand(p);
#         case '$':
#             return picolParseVar(p);
#         case '#':
#             if (p->type == PT_EOL) {
#                 picolParseComment(p);
#                 continue;
#             }
#             return picolParseString(p);
#         default:
#             return picolParseString(p);
#         }
#     }
#     return PICOL_OK; /* unreached */
# }
def picolGetToken(p):
    while True:
        # if not p.len:
        if p.p >= len(p.text) or not p.len:
            if p.type != PT_EOL and p.type != PT_EOF:
                p.type = PT_EOL
            else:
                p.type = PT_EOF
            return PICOL_OK

        c = p.text[p.p]
        if c == ' ' or c == '\t' or c == '\r':
            if p.insidequote:
                return picolParseString(p)
            return picolParseSep(p)
        elif c == '\n' or c == ';':
            if p.insidequote:
                return picolParseString(p)
            return picolParseEol(p)
        elif c == '[':
            return picolParseCommand(p)
        elif c == '$':
            return picolParseVar(p)
        elif c == '#':
            if p.type == PT_EOL:
                picolParseComment(p)
                continue
            return picolParseString(p)
        else:  # default
            return picolParseString(p)

    return PICOL_OK  # (unreached) ?

# void picolInitInterp(struct picolInterp *i) {
#     i->level = 0;
#     i->callframe = malloc(sizeof(struct picolCallFrame));
#     i->callframe->vars = NULL;
#     i->callframe->parent = NULL;
#     i->commands = NULL;
#     i->result = strdup("");
# }
def picolInitInterp(i):
    i.level = 0
    i.callframe = PicolCallFrame()
    i.callframe.vars = None
    i.callframe.parent = None
    i.commands = None
    i.result = ""


# void picolSetResult(struct picolInterp *i, char *s) {
#     free(i->result);
#     i->result = strdup(s);
# }
def picolSetResult(i, s):
    i.result = s


# struct picolVar *picolGetVar(struct picolInterp *i, char *name) {
#     struct picolVar *v = i->callframe->vars;
#     while(v) {
#         if (strcmp(v->name,name) == 0) return v;
#         v = v->next;
#     }
#     return NULL;
# }
def picolGetVar(i, name):
    v = i.callframe.vars
    while v:
        if v.name == name: return v
        v = v.next
    return None


# int picolSetVar(struct picolInterp *i, char *name, char *val) {
#     struct picolVar *v = picolGetVar(i,name);
#     if (v) {
#         free(v->val);
#         v->val = strdup(val);
#     } else {
#         v = malloc(sizeof(*v));
#         v->name = strdup(name);
#         v->val = strdup(val);
#         v->next = i->callframe->vars;
#         i->callframe->vars = v;
#     }
#     return PICOL_OK;
# }
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


# struct picolCmd *picolGetCommand(struct picolInterp *i, char *name) {
#     struct picolCmd *c = i->commands;
#     while(c) {
#         if (strcmp(c->name,name) == 0) return c;
#         c = c->next;
#     }
#     return NULL;
# }
def picolGetCommand(i, name):
    c = i.commands
    while c:
        if c.name == name: return c
        c = c.next
    return None


# int picolRegisterCommand(struct picolInterp *i, char *name, picolCmdFunc f, void *privdata) {
#     struct picolCmd *c = picolGetCommand(i,name);
#     char errbuf[1024];
#     if (c) {
#         snprintf(errbuf,1024,"Command '%s' already defined",name);
#         picolSetResult(i,errbuf);
#         return PICOL_ERR;
#     }
#     c = malloc(sizeof(*c));
#     c->name = strdup(name);
#     c->func = f;
#     c->privdata = privdata;
#     c->next = i->commands;
#     i->commands = c;
#     return PICOL_OK;
# }
def picolRegisterCommand(i, name, f, privdata):
    c = picolGetCommand(i, name)
    # errbuf = None
    if c:
        errbuf = "Command '%s' already defined" % name
        picolSetResult(i, errbuf)
        return PICOL_ERR

    c = PicolCmd()
    c.name = name
    c.func = f
    c.privdata = privdata
    c.next = i.commands
    i.commands = c
    return PICOL_OK


# /* EVAL! */
# int picolEval(struct picolInterp *i, char *t) {
#     struct picolParser p;
#     int argc = 0, j;
#     char **argv = NULL;
#     char errbuf[1024];
#     int retcode = PICOL_OK;
#     picolSetResult(i,"");
#     picolInitParser(&p,t);
#     while(1) {
#         char *t;
#         int tlen;
#         int prevtype = p.type;
#         picolGetToken(&p);
#         if (p.type == PT_EOF) break;
#         tlen = p.end-p.start+1;
#         if (tlen < 0) tlen = 0;
#         t = malloc(tlen+1);
#         memcpy(t, p.start, tlen);
#         t[tlen] = '\0';
#         if (p.type == PT_VAR) {
#             struct picolVar *v = picolGetVar(i,t);
#             if (!v) {
#                 snprintf(errbuf,1024,"No such variable '%s'",t);
#                 free(t);
#                 picolSetResult(i,errbuf);
#                 retcode = PICOL_ERR;
#                 goto err;
#             }
#             free(t);
#             t = strdup(v->val);
#         } else if (p.type == PT_CMD) {
#             retcode = picolEval(i,t);
#             free(t);
#             if (retcode != PICOL_OK) goto err;
#             t = strdup(i->result);
#         } else if (p.type == PT_ESC) {
#             /* XXX: escape handling missing! */
#         } else if (p.type == PT_SEP) {
#             prevtype = p.type;
#             free(t);
#             continue;
#         }
#         /* We have a complete command + args. Call it! */
#         if (p.type == PT_EOL) {
#             struct picolCmd *c;
#             free(t);
#             prevtype = p.type;
#             if (argc) {
#                 if ((c = picolGetCommand(i,argv[0])) == NULL) {
#                     snprintf(errbuf,1024,"No such command '%s'",argv[0]);
#                     picolSetResult(i,errbuf);
#                     retcode = PICOL_ERR;
#                     goto err;
#                 }
#                 retcode = c->func(i,argc,argv,c->privdata);
#                 if (retcode != PICOL_OK) goto err;
#             }
#             /* Prepare for the next command */
#             for (j = 0; j < argc; j++) free(argv[j]);
#             free(argv);
#             argv = NULL;
#             argc = 0;
#             continue;
#         }
#         /* We have a new token, append to the previous or as new arg? */
#         if (prevtype == PT_SEP || prevtype == PT_EOL) {
#             argv = realloc(argv, sizeof(char*)*(argc+1));
#             argv[argc] = t;
#             argc++;
#         } else { /* Interpolation */
#             int oldlen = strlen(argv[argc-1]), tlen = strlen(t);
#             argv[argc-1] = realloc(argv[argc-1], oldlen+tlen+1);
#             memcpy(argv[argc-1]+oldlen, t, tlen);
#             argv[argc-1][oldlen+tlen]='\0';
#             free(t);
#         }
#         prevtype = p.type;
#     }
# err:
#     for (j = 0; j < argc; j++) free(argv[j]);
#     free(argv);
#     return retcode;
# }
def picolEval(i, t):
    p = PicolParser()
    argc = 0
    j = None
    argv = []
    errbuf = None
    retcode = PICOL_OK
    picolSetResult(i, "")
    picolInitParser(p, t)
    while True:
        t = None
        tlen = None
        prevtype = p.type
        picolGetToken(p)
        if p.type == PT_EOF:
            break
        tlen = p.end - p.start + 1
        if tlen < 0:
            tlen = 0
        t = p.text[p.start:p.start+tlen]
        if p.type == PT_VAR:
            v = picolGetVar(i, t)
            if not v:
                errbuf = "No such variable '%s'" % t
                picolSetResult(i, errbuf)
                retcode = PICOL_ERR
                break  # goto err

            t = v.val
        elif p.type == PT_CMD:
            retcode = picolEval(i, t)
            if retcode != PICOL_OK:
                break  # Goto err
            t = i.result
        elif p.type == PT_ESC:
            pass  # escape handling missing
        elif p.type == PT_SEP:
            prevtype = p.type
            continue

        # We have a complete command + args. Call it!
        if p.type == PT_EOL:
            c = PicolCmd()
            prevtype = p.type
            if argc:
                c = picolGetCommand(i, argv[0])
                if c == None:
                    errbuf = "No such command '%s'" % argv[0]
                    picolSetResult(i, errbuf)
                    retcode = PICOL_ERR
                    break  # goto err
                retcode = c.func(i, argc, argv, c.privdata)
                if retcode != PICOL_OK:
                    break  # goto err

            # Prepare for the next command
            argv = []
            argc = 0
            continue

        # We have a new token, append to the previous or as new arg?
        if prevtype == PT_SEP or prevtype == PT_EOL:
            argv.append(t)
            argc += 1
        else:  # Interpolation
            oldlen = len(argv[argc - 1])
            tlen = len(t)
            argv[argc-1] += t[0:tlen]

        prevtype = p.type

# err:
    return retcode


# /* ACTUAL COMMANDS! */
# int picolArityErr(struct picolInterp *i, char *name) {
#     char buf[1024];
#     snprintf(buf,1024,"Wrong number of args for %s",name);
#     picolSetResult(i,buf);
#     return PICOL_ERR;
# }
def picolArityErr(i, name):
    buf = ""
    buf = "Wrong number of args for %s" % name
    picolSetResult(i, buf)
    return PICOL_ERR


# int picolCommandMath(struct picolInterp *i, int argc, char **argv, void *pd) {
#     char buf[64]; int a, b, c;
#     if (argc != 3) return picolArityErr(i,argv[0]);
#     a = atoi(argv[1]); b = atoi(argv[2]);
#     if (argv[0][0] == '+') c = a+b;
#     else if (argv[0][0] == '-') c = a-b;
#     else if (argv[0][0] == '*') c = a*b;
#     else if (argv[0][0] == '/') c = a/b;
#     else if (argv[0][0] == '>' && argv[0][1] == '\0') c = a > b;
#     else if (argv[0][0] == '>' && argv[0][1] == '=') c = a >= b;
#     else if (argv[0][0] == '<' && argv[0][1] == '\0') c = a < b;
#     else if (argv[0][0] == '<' && argv[0][1] == '=') c = a <= b;
#     else if (argv[0][0] == '=' && argv[0][1] == '=') c = a == b;
#     else if (argv[0][0] == '!' && argv[0][1] == '=') c = a != b;
#     else c = 0; /* I hate warnings */
#     snprintf(buf,64,"%d",c);
#     picolSetResult(i,buf);
#     return PICOL_OK;
# }
def picolCommandMath(i, argc, argv, pd):
    buf, a, b, c = None, None, None, None
    if argc != 3: return picolArityErr(i, argv[0])
    a = int(argv[1])
    b = int(argv[2])
    if len(argv[0]) == 1: # then add 1 space to kind of keep format of c code
        argv[0] += ' '
    if argv[0][0] == '+': c = a + b
    elif argv[0][0] == '-': c = a + b
    elif argv[0][0] == '*': c = a * b
    elif argv[0][0] == '/': c = a // b
    elif argv[0][0] == '>' and argv[0][1] == ' ': c = 1 if a > b else 0
    elif argv[0][0] == '>' and argv[0][1] == '=': c = 1 if a >= b else 0
    elif argv[0][0] == '<' and argv[0][1] == ' ': c = 1 if a < b else 0
    elif argv[0][0] == '<' and argv[0][1] == '=': c = 1 if a <= b else 0
    elif argv[0][0] == '=' and argv[0][1] == '=': c = 1 if a == b else 0
    elif argv[0][0] == '!' and argv[0][1] == '=': c = 1 if a != b else 0
    else: c = 0   # prevent warnings in original code?
    buf = str(c)
    picolSetResult(i, buf)
    return PICOL_OK

# int picolCommandSet(struct picolInterp *i, int argc, char **argv, void *pd) {
#     if (argc != 3) return picolArityErr(i,argv[0]);
#     picolSetVar(i,argv[1],argv[2]);
#     picolSetResult(i,argv[2]);
#     return PICOL_OK;
# }
def picolCommandSet(i, argc, argv, pd):
    if argc != 3: return picolArityErr(i, argv[0])
    picolSetVar(i, argv[1], argv[2])
    picolSetResult(i, argv[2])
    return PICOL_OK


# int picolCommandPuts(struct picolInterp *i, int argc, char **argv, void *pd) {
#     if (argc != 2) return picolArityErr(i,argv[0]);
#     printf("%s\n", argv[1]);
#     return PICOL_OK;
# }
def picolCommandPuts(i, argc, argv, pd):
    if argc != 2: return picolArityErr(i, argv[0])
    print("%s" % argv[1])
    return PICOL_OK


# int picolCommandIf(struct picolInterp *i, int argc, char **argv, void *pd) {
#     int retcode;
#     if (argc != 3 && argc != 5) return picolArityErr(i,argv[0]);
#     if ((retcode = picolEval(i,argv[1])) != PICOL_OK) return retcode;
#     if (atoi(i->result)) return picolEval(i,argv[2]);
#     else if (argc == 5) return picolEval(i,argv[4]);
#     return PICOL_OK;
# }
def picolCommandIf(i, argc, argv, pd):
    retcode = None
    if argc != 3 and argc != 5:
        return picolArityErr(i, argv[0])

    retcode = picolEval(i, argv[1])
    if retcode != PICOL_OK:
        return retcode

    # if i.result.isdecimal() and int(i.result):
    # if bool(i.result):
    if int(i.result):
        return picolEval(i, argv[2])
    elif argc == 5:
        return picolEval(i, argv[4])

    return PICOL_OK


# int picolCommandWhile(struct picolInterp *i, int argc, char **argv, void *pd) {
#     if (argc != 3) return picolArityErr(i,argv[0]);
#     while(1) {
#         int retcode = picolEval(i,argv[1]);
#         if (retcode != PICOL_OK) return retcode;
#         if (atoi(i->result)) {
#             if ((retcode = picolEval(i,argv[2])) == PICOL_CONTINUE) continue;
#             else if (retcode == PICOL_OK) continue;
#             else if (retcode == PICOL_BREAK) return PICOL_OK;
#             else return retcode;
#         } else {
#             return PICOL_OK;
#         }
#     }
# }
def picolCommandWhile(i, argc, argv, pd):
    if argc != 3: return picolArityErr(i, argv[0])
    while True:
        retcode = picolEval(i, argv[1])
        if retcode != PICOL_OK:
            return retcode
        if int(i.result):
            retcode = picolEval(i, argv[2])
            if retcode == PICOL_CONTINUE:
                continue
            elif retcode == PICOL_OK:
                continue
            elif retcode == PICOL_BREAK:
                return PICOL_OK
            else:
                return retcode
        else:
            return PICOL_OK


# int picolCommandRetCodes(struct picolInterp *i, int argc, char **argv, void *pd) {
#     if (argc != 1) return picolArityErr(i,argv[0]);
#     if (strcmp(argv[0],"break") == 0) return PICOL_BREAK;
#     else if (strcmp(argv[0],"continue") == 0) return PICOL_CONTINUE;
#     return PICOL_OK;
# }
def picolCommandRetCodes(i, argc, argv, pd):
    if argc != 1: return picolArityErr(i, argv[0])
    if argv[0] == "break":
        return PICOL_BREAK
    elif argv[0] == "continue":
        return PICOL_CONTINUE
    return PICOL_OK


# void picolDropCallFrame(struct picolInterp *i) {
#     struct picolCallFrame *cf = i->callframe;
#     struct picolVar *v = cf->vars, *t;
#     while(v) {
#         t = v->next;
#         free(v->name);
#         free(v->val);
#         free(v);
#         v = t;
#     }
#     i->callframe = cf->parent;
#     free(cf);
# }
def picolDropCallFrame(i):
    cf = i.callframe
    v = cf.vars
    t = None
    while v:
        t = v.next
        v = t
    i.callframe = cf.parent


# int picolCommandCallProc(struct picolInterp *i, int argc, char **argv, void *pd) {
#     char **x=pd, *alist=x[0], *body=x[1], *p=strdup(alist), *tofree;
#     struct picolCallFrame *cf = malloc(sizeof(*cf));
#     int arity = 0, done = 0, errcode = PICOL_OK;
#     char errbuf[1024];
#     cf->vars = NULL;
#     cf->parent = i->callframe;
#     i->callframe = cf;
#     tofree = p;
#     while(1) {
#         char *start = p;
#         while(*p != ' ' && *p != '\0') p++;
#         if (*p != '\0' && p == start) {
#             p++; continue;
#         }
#         if (p == start) break;
#         if (*p == '\0') done=1; else *p = '\0';
#         if (++arity > argc-1) goto arityerr;
#         picolSetVar(i,start,argv[arity]);
#         p++;
#         if (done) break;
#     }
#     free(tofree);
#     if (arity != argc-1) goto arityerr;
#     errcode = picolEval(i,body);
#     if (errcode == PICOL_RETURN) errcode = PICOL_OK;
#     picolDropCallFrame(i); /* remove the called proc callframe */
#     return errcode;
# arityerr:
#     snprintf(errbuf,1024,"Proc '%s' called with wrong arg num",argv[0]);
#     picolSetResult(i,errbuf);
#     picolDropCallFrame(i); /* remove the called proc callframe */
#     return PICOL_ERR;
# }
def picolCommandCallProc(i, argc, argv, pd):
    x = pd
    aList = x[0]
    body = x[1]
    p = aList
    # tofree -- not needed?
    cf = PicolCallFrame()
    arity = 0
    done = 0
    errcode = PICOL_OK
    errbuf = ''
    cf.vars = None
    cf.parent = i.callframe
    i.callframe = cf
    try:
        while True:
            start = 0
            pp = 0
            while pp < len(p) and p[pp] != ' ': pp += 1
            if pp < len(p) and pp == start:
                pp += 1
                continue
            if pp == start: break
            if pp == len(p):
                done = 1
            else:
                p = p[:pp]
            arity += 1
            if arity > argc - 1: raise ArityErr()
            # picolSetVar(i, start, argv[arity])
            picolSetVar(i, p, argv[arity])
            pp += 1
            if done:
                break

        if arity != argc - 1: raise ArityErr()
        errcode = picolEval(i, body)
        if errcode == PICOL_RETURN:
            errcode = PICOL_OK
        picolDropCallFrame(i)  # remove the called proc callframe
        return errcode
    except ArityErr:
        errbuf = "Proc '%s' called with wrong arg num" % argv[0]
        picolSetResult(i, errbuf)
        picolDropCallFrame(i)  # remove the called proc call frame
        return PICOL_ERR


# int picolCommandProc(struct picolInterp *i, int argc, char **argv, void *pd) {
#     char **procdata = malloc(sizeof(char*)*2);
#     if (argc != 4) return picolArityErr(i,argv[0]);
#     procdata[0] = strdup(argv[2]); /* arguments list */
#     procdata[1] = strdup(argv[3]); /* procedure body */
#     return picolRegisterCommand(i,argv[1],picolCommandCallProc,procdata);
# }
def picolCommandProc(i, argc, argv, pd):
    procdata = []
    if argc != 4:
        return picolArityErr(i, argv[0])
    # procdata[0] = argv[2]  # arguments list
    procdata.append(argv[2])
    # procdata[1] = argv[3]  # procedure body
    procdata.append(argv[3])
    return picolRegisterCommand(i, argv[1], picolCommandCallProc, procdata)


# int picolCommandReturn(struct picolInterp *i, int argc, char **argv, void *pd) {
#     if (argc != 1 && argc != 2) return picolArityErr(i,argv[0]);
#     picolSetResult(i, (argc == 2) ? argv[1] : "");
#     return PICOL_RETURN;
# }
def picolCommandReturn(i, argc, argv, pd):
    if argc != 1 and argc != 2:
        return picolArityErr(i, argv[0])
    picolSetResult(i, argv[1] if argc == 2 else "")
    return PICOL_RETURN


# void picolRegisterCoreCommands(struct picolInterp *i) {
#     int j; char *name[] = {"+","-","*","/",">",">=","<","<=","==","!="};
#     for (j = 0; j < (int)(sizeof(name)/sizeof(char*)); j++)
#         picolRegisterCommand(i,name[j],picolCommandMath,NULL);
#     picolRegisterCommand(i,"set",picolCommandSet,NULL);
#     picolRegisterCommand(i,"puts",picolCommandPuts,NULL);
#     picolRegisterCommand(i,"if",picolCommandIf,NULL);
#     picolRegisterCommand(i,"while",picolCommandWhile,NULL);
#     picolRegisterCommand(i,"break",picolCommandRetCodes,NULL);
#     picolRegisterCommand(i,"continue",picolCommandRetCodes,NULL);
#     picolRegisterCommand(i,"proc",picolCommandProc,NULL);
#     picolRegisterCommand(i,"return",picolCommandReturn,NULL);
# }
def picolRegisterCoreCommands(i):
    name = ["+", "-", "*", "/", ">", ">=", "<", "<=", "==", "!="]
    for j in name:
        picolRegisterCommand(i, j, picolCommandMath, None)
    picolRegisterCommand(i, "set", picolCommandSet, None)
    picolRegisterCommand(i, "puts", picolCommandPuts, None)
    picolRegisterCommand(i, "if", picolCommandIf, None)
    picolRegisterCommand(i, "while", picolCommandWhile, None)
    picolRegisterCommand(i, "break", picolCommandRetCodes, None)
    picolRegisterCommand(i, "continue", picolCommandRetCodes, None)
    picolRegisterCommand(i, "proc", picolCommandProc, None)
    picolRegisterCommand(i, "return", picolCommandReturn, None)


# int main(int argc, char **argv) {
#     struct picolInterp interp;
#     picolInitInterp(&interp);
#     picolRegisterCoreCommands(&interp);
#     if (argc == 1) {
#         while(1) {
#             char clibuf[1024];
#             int retcode;
#             printf("picol> "); fflush(stdout);
#             if (fgets(clibuf,1024,stdin) == NULL) return 0;
#             retcode = picolEval(&interp,clibuf);
#             if (interp.result[0] != '\0')
#                 printf("[%d] %s\n", retcode, interp.result);
#         }
#     } else if (argc == 2) {
#         char buf[1024*16];
#         FILE *fp = fopen(argv[1],"r");
#         if (!fp) {
#             perror("open"); exit(1);
#         }
#         buf[fread(buf,1,1024*16,fp)] = '\0';
#         fclose(fp);
#         if (picolEval(&interp,buf) != PICOL_OK) printf("%s\n", interp.result);
#     }
#     return 0;
# }
def main():
    import sys

    interp = PicolInterp()
    picolInitInterp(interp)
    picolRegisterCoreCommands(interp)
    while True:
        clibuf = None
        retcode = None
        clibuf = input('picol> ')
        if clibuf == None:
            sys.exit()
        retcode = picolEval(interp, clibuf)
        if interp.result and interp.result[0] != PICOL_OK:
            print("[%d] %s" % (retcode, interp.result))


if __name__ == '__main__':
    main()