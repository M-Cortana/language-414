import re

def StateType(x):
        if re.search(r"^ *while.*: *$", x) != None:
                return "WHILE"
        if re.search(r"^ *if .*(<=|>=|==|!=|<|>|).*: *$", x) != None:
                return "IF"
        if re.search(r"^ *else: *$", x) != None:
                return "ELSE"
        if re.search(r"^ *#.*$", x) != None:
                return "COMMENT"
        if re.search(r"^ *continue *$", x) != None:
                return "CONTINUE"
        if re.search(r"^ *break *$", x) != None:
                return "BREAK"
        if re.search(r"^\s*$", x) != None:
                return "BLANK"
        if re.search(r"^ *assign.*reg\([a-zA-Z0-9]+\).*", x) != None:
                return "ASSREG"
        return "OTHER"

def Indent(x):
        if re.search(r"^ *", x) != None:
                return len(re.search(r"^ *", x).group())
        else:
                return 0

def WhileCondition(x):
        return re.search(r"(?<=while).*(?=: *$)", x).group()

def AssignTarget(x):
        return re.search(r"^ *(([a-z0-9A-Z]+ *\[[a-z0-9A-Z]+\])|([a-zA-Z]+\w*))(?= *(=|\+=|-=|\*=|\/=|<<=|>>=))", x).group().strip()

def AssignType(x):
        return re.search(r"(=|\+=|-=|\*=|\/=|<<=|>>=)", x).group().strip()

def AssignSource(x):
        return re.search(r"(?<==).*$", x).group().strip()

def IfCondition(x):
        return re.search(r"(?<=if).*(?=: *$)", x).group()

def AssReg(x):
        return re.search(r"(?<=reg\()[a-zA-Z0-9]+(?=\))", x).group().strip()

def AssVar(x):
        return re.search(r"([a-zA-Z0-9]+ *(?==))|([a-zA-Z0-9]+ *$)", x).group().strip()

def CommentContent(x):
        return re.search(r"(?<=#).*", x).group()