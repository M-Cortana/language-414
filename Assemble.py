import SyntaxTree as st
import re

tmpLabelCnt = -1

def newLabelNum():
        global tmpLabelCnt
        tmpLabelCnt += 1
        return tmpLabelCnt

def findANum(used):
        i = 0
        while i in used:
                i += 1
        return i

def findResNum(x):
        if type(x) != type("0"):
                return None
        if re.search(r"(?<=^__res)[0-9]+(?=__)", x) != None:
                return int(re.search(r"(?<=^__res)[0-9]+(?=__)", x).group())
        return None

def findTmpldNum(x):
        if type(x) != type("0"):
                return None
        if re.search(r"(?<=^__tmpld)[0-9]+(?=__)", x) != None:
                return int(re.search(r"(?<=^__tmpld)[0-9]+(?=__)", x).group())
        return None


def RPNCalculator(r):
        stack = []
        inss = []
        resUsed = []
        #print(r)
        for i in r:
                isVar = False
                if re.search(r"^[a-zA-Z]+[0-9a-zA-Z]*", i) != None and i != "or" and i != "and":
                        stack.append(i)
                        isVar = True
                if i.isdigit():
                        stack.append(int(i))
                        isVar = True
                if i == "True":
                        stack.append(True)
                        isVar = True
                if i == "False":
                        stack.append(False)
                        isVar = True
                if isVar == False:
                        if findResNum(stack[-1]) != None and findResNum(stack[-1]) in resUsed:
                                resUsed.remove(findResNum(stack[-1]))
                        b = stack[-1]
                        stack.pop()
                        #if len(stack) == 0:
                                #print(i)
                        if findResNum(stack[-1]) != None and findResNum(stack[-1]) in resUsed:
                                resUsed.remove(findResNum(stack[-1]))
                        a = stack[-1]
                        stack.pop()
                        rn = findANum(resUsed)
                        resUsed.append(rn)
                        if type(a) == type("0") and re.search(r"[a-zA-Z0-9]+\[[a-zA-Z0-9]+]", a) != None:
                                #A is an Array
                                base = re.search(r"[a-zA-Z0-9]+(?=\[[a-zA-Z0-9]+])", a).group().strip()
                                bias = re.search(r"(?<=\[)[a-zA-Z0-9]+(?=\])", a).group().strip()
                                if bias.isdigit():
                                        if base.isdigit():
                                                inss.append("addi %%(__array__), x0, %s" % (base))
                                                inss.append("lw %%(__tmpld%d__), %s(%%(__array__))" % (0, bias))
                                        else:
                                                inss.append("lw %%(__tmpld%d__), %s(%%(%s))" % (0, bias, base))
                                else:
                                        if base.isdigit():
                                                inss.append("lw %%(__tmpld%d__), %s(%%(%s))" % (0, base, bias))
                                        else:
                                                inss.append("add %%(__array__), %%(%s), %%(%s)" % (bias, base))
                                                inss.append("lw %%(__tmpld%d__), 0(%%(__array__))" % (0))
                                a = "__tmpld%d__" % (0)
                        if type(b) == type("0") and re.search(r"[a-zA-Z0-9]+\[[a-zA-Z0-9]+]", b) != None:
                                #A is an Array
                                base = re.search(r"[a-zA-Z0-9]+(?=\[[a-zA-Z0-9]+])", b).group().strip()
                                bias = re.search(r"(?<=\[)[a-zA-Z0-9]+(?=\])", b).group().strip()
                                if bias.isdigit():
                                        if base.isdigit():
                                                inss.append("addi %%(__array__), x0, %s" % (base))
                                                inss.append("lw %%(__tmpld%d__), %s(%%(__array__))" % (1, bias))
                                        else:
                                                inss.append("lw %%(__tmpld%d__), %s(%%(%s))" % (1, bias, base))
                                else:
                                        if base.isdigit():
                                                inss.append("lw %%(__tmpld%d__), %s(%%(%s))" % (1, base, bias))
                                        else:
                                                inss.append("add %%(__array__), %%(%s), %%(%s)" % (bias, base))
                                                inss.append("lw %%(__tmpld%d__), 0(%%(__array__))" % (1))
                                b = "__tmpld%d__" % (1)
                        if i == "+":
                                #res = a + b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a + b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__res%d__), %%(%s), %d" % (rn, b, a))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("add %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "-":
                                #res = a - b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a - b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("sub %%(__res%d__), %%(__tmp__), %%(%s)" % (rn, b))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("sub %%(__res%d__), %%(%s), %%(__tmp__)" % (rn, a))
                                        else:
                                                inss.append("sub %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "*":
                                #res = a * b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a * b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("mul %%(__res%d__), %%(__tmp__), %%(%s)" % (rn, b))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("mul %%(__res%d__), %%(%s), %%(__tmp__)" % (rn, a))
                                        else:
                                                inss.append("mul %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "/":
                                #res = a / b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a / b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("div %%(__res%d__), %%(__tmp__), %%(%s)" % (rn, b))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("div %%(__res%d__), %%(%s), %%(__tmp__)" % (rn, a))
                                        else:
                                                inss.append("div %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "<<":
                                #res = a << b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a << b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("slli %%(__res%d__), %%(__tmp__), %%(%s)" % (rn, b))
                                else:
                                        if type(b) == type(0):
                                                inss.append("slli %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("sll %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == ">>":
                                #res = a >> b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a >> b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("srai %%(__res%d__), %%(__tmp__), %%(%s)" % (rn, b))
                                else:
                                        if type(b) == type(0):
                                                inss.append("srai %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("sra %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "&":
                                #res = a & b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a & b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("andi %%(__res%d__), %%(%s), %d" % (rn, b, a))
                                else:
                                        if type(b) == type(0):
                                                inss.append("andi %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("and %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "|":
                                #res = a | b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a | b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("ori %%(__res%d__), %%(%s), %d" % (rn, b, a))
                                else:
                                        if type(b) == type(0):
                                                inss.append("ori %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("or %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "^":
                                #res = a ^ b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a ^ b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("xori %%(__res%d__), %%(%s), %d" % (rn, b, a))
                                else:
                                        if type(b) == type(0):
                                                inss.append("xori %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("xor %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "==":
                                #res = a == b ? 1, 0
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = 1 if a == b else 0
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bne %%(__tmp__), %%(%s), BTMP%d" % (b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bne %%(__tmp__), %%(%s), BTMP%d" % (a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                        else:
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bne %%(%s), %%(%s), BTMP%d" % (a, b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                        if i == "!=":
                                #res = a != b ? 1, 0
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = 1 if a != b else 0
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("beq %%(__tmp__), %%(%s), BTMP%d" % (b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("beq %%(__tmp__), %%(%s), BTMP%d" % (a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                        else:
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("beq %%(%s), %%(%s), BTMP%d" % (a, b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                        if i == ">":
                                #res = a > b ? 1, 0
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = 1 if a > b else 0
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bge %%(%s), %%(__tmp__), BTMP%d" % (b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bge %%(__tmp__), %%(%s), BTMP%d" % (a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                        else:
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bge %%(%s), %%(%s), BTMP%d" % (b, a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                        if i == "<":
                                #res = a < b ? 1, 0
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = 1 if a < b else 0
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bge %%(__tmp__), %%(%s) , BTMP%d" % (b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bge %%(%s), %%(__tmp__), BTMP%d" % (a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                        else:
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("bge %%(%s), %%(%s), BTMP%d" % (a, b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                        if i == "<=":
                                #res = a <= b ? 1, 0
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = 1 if a <= b else 0
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("blt %%(%s), %%(__tmp__), BTMP%d" % (b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("blt %%(__tmp__), %%(%s), BTMP%d" % (a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                        else:
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("blt %%(%s), %%(%s), BTMP%d" % (b, a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                        if i == ">=":
                                #res = a >= b ? 1: 0
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = 1 if a >= b else 0
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("addi %%(__tmp__), x0, %d" % (a))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("blt %%(__tmp__), %%(%s) , BTMP%d" % (b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                else:
                                        if type(b) == type(0):
                                                inss.append("addi %%(__tmp__), x0, %d" % (b))
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("blt %%(%s), %%(__tmp__), BTMP%d" % (a, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                                        else:
                                                inss.append("addi %%(__res%d__), x0, 0" % (rn))
                                                inss.append("blt %%(%s), %%(%s), BTMP%d" % (a, b, newLabelNum()))
                                                inss.append("addi %%(__res%d__), x0, 1" % (rn))
                                                inss.append("BTMP%d:" % (tmpLabelCnt))
                        if i == "and":
                                #res = a and b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a & b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("andi %%(__res%d__), %%(%s), %d" % (rn, b, a))
                                else:
                                        if type(b) == type(0):
                                                inss.append("andi %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("and %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        if i == "or":
                                #res = a or b
                                if type(a) == type(0):
                                        if type(b) == type(0):
                                                r = a | b
                                                inss.append("addi %%(__res%d__), x0, %d" % (rn, r))
                                        else:
                                                inss.append("ori %%(__res%d__), %%(%s), %d" % (rn, b, a))
                                else:
                                        if type(b) == type(0):
                                                inss.append("ori %%(__res%d__), %%(%s), %d" % (rn, a, b))
                                        else:
                                                inss.append("or %%(__res%d__), %%(%s), %%(%s)" % (rn, a, b))
                        stack.append("__res%d__" % (rn))
        return [inss, stack[-1]]


whileLabelCnt = -1
lastWhileCnt = 0
def newWhileLabelNum():
        global whileLabelCnt
        whileLabelCnt += 1
        return whileLabelCnt


Instructions = []
def appendInsts(inss):
        for i in inss:
                Instructions.append(i)

def ParseSyntaxTree(node):
        global lastWhileCnt
        if node.type == "ASSIGN":
                vName = node.Childs[0].Contents[0]
                rpn = node.Childs[1].Contents[0]
                cr = RPNCalculator(rpn)
                appendInsts(cr[0])
                isArray = False
                if re.search(r"[a-z0-9A-Z]+ *\[[a-z0-9A-Z]+\]", vName) != None:
                        #Target is an array
                        AName = vName
                        vName = "__tmpsd__"
                        isArray = True
                if type(cr[1]) == type(0):
                        if node.Contents[0] == "=":
                                Instructions.append("addi %%(%s), x0, %d" % (vName, cr[1]))
                        if node.Contents[0] == "+=":
                                Instructions.append("addi %%(%s), %%(%s), %d" % (vName, vName, cr[1]))
                else:
                        if node.Contents[0] == "=":
                                Instructions.append("add %%(%s), x0, %%(%s)" % (vName, cr[1]))
                        if node.Contents[0] == "+=":
                                Instructions.append("add %%(%s), %%(%s), %%(%s)" % (vName, vName, cr[1]))
                        if node.Contents[0] == "-=":
                                Instructions.append("sub %%(%s), %%(%s), %%(%s)" % (vName, vName, cr[1]))
                        if node.Contents[0] == "*=":
                                Instructions.append("mul %%(%s), %%(%s), %%(%s)" % (vName, vName, cr[1]))
                        if node.Contents[0] == "/=":
                                Instructions.append("div %%(%s), %%(%s), %%(%s)" % (vName, vName, cr[1]))
                        if node.Contents[0] == "<<=":
                                Instructions.append("sll %%(%s), %%(%s), %%(%s)" % (vName, vName, cr[1]))
                        if node.Contents[0] == ">>=":
                                Instructions.append("sra %%(%s), %%(%s), %%(%s)" % (vName, vName, cr[1]))
                if isArray:
                        #Target is an array
                        base = re.search(r"[a-zA-Z0-9]+(?=\[[a-zA-Z0-9]+])", AName).group().strip()
                        bias = re.search(r"(?<=\[)[a-zA-Z0-9]+(?=\])", AName).group().strip()
                        if bias.isdigit():
                                if base.isdigit():
                                        Instructions.append("addi %%(__array__), x0, %s" % (base))
                                        Instructions.append("sw %%(__tmpsd__), %s(%%(__array__))" % (bias))
                                else:
                                        Instructions.append("sw %%(__tmpsd__), %s(%%(%s))" % (bias, base))
                        else:
                                if base.isdigit():
                                        Instructions.append("sw %%(__tmpsd__), %s(%%(%s))" % (base, bias))
                                else:
                                        Instructions.append("add %%(__array__), %%(%s), %%(%s)" % (bias, base))
                                        Instructions.append("sw %(__tmpsd__), 0(%(__array__))")
                return
        if node.type == "WHILE":
                cond = node.Childs[0].Contents[0]
                cr = RPNCalculator(cond)
                ln = newWhileLabelNum()
                lastWhileCnt = ln
                Instructions.append("LOOP%d:" % (ln))
                appendInsts(cr[0])
                Instructions.append("beq %%(%s), x0, END%d" % (cr[1], ln))
                ParseSyntaxTree(node.Childs[1])
                Instructions.append("beq x0, x0, LOOP%d" % (ln))
                Instructions.append("END%d:" % (ln))
                return
        if node.type == "IF":
                cond = node.Childs[0].Contents[0]
                cr = RPNCalculator(cond)
                ln = newWhileLabelNum()
                appendInsts(cr[0])
                if len(node.Childs) < 3:        #If without else
                        Instructions.append("beq %%(%s), x0, END%d" % (cr[1], ln))
                        ParseSyntaxTree(node.Childs[1])
                        Instructions.append("END%d:" % (ln))
                else:   #If with else
                        Instructions.append("beq %%(%s), x0, ELSE%d" % (cr[1], ln))
                        ParseSyntaxTree(node.Childs[1])
                        Instructions.append("beq x0, x0, END%d" % (ln))
                        Instructions.append("ELSE%d:" % (ln))
                        ParseSyntaxTree(node.Childs[2])
                        Instructions.append("END%d:" % (ln))
                return
        if node.type == "ASSREG":
                r = node.Childs[0].Contents[0]
                v = node.Childs[1].Contents[0]
                Instructions.append("assign reg(%s), %%(%s)" % (r, v))
                return
        if node.type == "COMMENT":
                Instructions.append("//%s" % (node.Contents[0]))
        if node.type == "BREAK":
                Instructions.append("beq x0, x0, END%d" %(lastWhileCnt))
        if node.type == "CONTINUE":
                Instructions.append("beq x0, x0, LOOP%d" %(lastWhileCnt))
                

        for i in node.Childs:
                ParseSyntaxTree(i)