import StatementParser as sp
import re
class node:
        Childs = []
        #while: [condition(rpn), body(body)]
        #if:    [condition(rpn), if(body), else(body)]
        #assign:[tar(var), src(rpn)] #src is a Reverse Polish notation
        #assreg:[reg, var]
        #root:  [1, 2, 3, ..., N]

        Contents = []
        #while: [None]
        #if:    [None]
        #assign:[type]
        #asreg: [None]
        #var:   [name]
        #rpn:   [[rpn]]
        #reg:   [name]
        #bop:   [bop]
        #comment:[comment]
        #break: [None]
        #continue: [None]

        Parameters = []
        def __init__(self, father, type, id):
                self.father = father
                self.type = type
                self.id = id
                self.Childs = []
                self.Contents = []

root = node(None, "BODY", -1)

stack = [['', -1]] #["WHILE", intend]
CurIntend = 0
CurNode = root
idCnt = 0
OpPri = {
        "and": 1,
        "or" : 1,
        "==": 5,
        "!=": 5,
        "<=": 5,
        ">=": 5,
        "<" : 5,
        ">" : 5,
        "+" : 10,
        "-" : 10,
        "*" : 20,
        "/" : 20,
        "&" : 30,
        "^" : 30,
        "|" : 30,
        "<<": 30,
        ">>": 30,
        "(" : -10
}

def GenRPN(x):
        stackOp = []
        stackNum = []
        res = []
        cur = 0
        while cur < len(x.rstrip()):
                srchNum = re.search(r"^ *(([0-9a-zA-Z]+\[[0-9a-zA-Z]+\])|[0-9a-zA-Z]+|True|False)", x[cur:])
                srchOp = re.search(r"^ *(\+|\-|\*|\/|\&|\^|\||\<<|\>>|or|and|!=|==|<=|>=|<|>)", x[cur:])
                srchBrac = re.search(r"^ *(\(|\))", x[cur:])
                #print("OP ", stackOp)
                #print("NUM", stackNum)
                #print("RES", res)
                #print(x[cur: ])
                if srchNum != None and srchNum.group().strip() != "and" and srchNum.group().strip() != "or":
                        stackNum.append(srchNum.group().strip())
                        cur += len(srchNum.group())
                        continue
                if srchBrac != None:
                        if srchBrac.group().strip() == "(":
                                stackOp.append(srchBrac.group().strip())
                        if srchBrac.group().strip() == ")":
                                for i in stackNum:
                                        res.append(i)
                                stackNum.clear()
                                while len(stackOp) != 0:
                                        if stackOp[-1] == "(":
                                                stackOp.pop()
                                                break
                                        else:
                                                res.append(stackOp[-1])
                                                stackOp.pop()
                        cur += len(srchBrac.group())
                        continue
                if srchOp != None:
                        if len(stackOp) != 0 and OpPri[srchOp.group().strip()] <= OpPri[stackOp[-1]]:
                                for i in stackNum:
                                        res.append(i)
                                stackNum.clear()
                                while len(stackOp) != 0:
                                        if OpPri[stackOp[-1]] < OpPri[srchOp.group().strip()]:
                                                #stackOp.append(srchOp.group().strip())
                                                break
                                        res.append(stackOp[-1])
                                        stackOp.pop()
                        stackOp.append(srchOp.group().strip())
                        cur += len(srchOp.group())
                        continue
        #print(stackNum)
        #print(stackOp)
        for i in stackNum:
                res.append(i)
        stackNum.clear()
        while len(stackOp) != 0:
                res.append(stackOp[-1])
                stackOp.pop()
        return res



def ConstructSyntaxTree(Lines):
        global idCnt
        CurNode = root
        for line in Lines:
                intend = sp.Indent(line)
                type = sp.StateType(line)
                while intend <= stack[-1][1] and type != "COMMENT":
                        CurNode = CurNode.father #Back to the While/If Node
                        CurNode = CurNode.father #Back to the Body Contained the If/While
                        stack.pop()

                if type == "ELSE":
                        CurNode = CurNode.Childs[-1] #Enter the If Node
                        CurNode.Childs.append(node(CurNode, "BODY", idCnt))
                        CurNode = CurNode.Childs[-1] #Enter the Else Child
                        idCnt += 1
                        stack.append(["ELSE", intend])


                if type == "OTHER":
                        rNode = CurNode
                        CurNode.Childs.append(node(CurNode, "ASSIGN", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the assign node
                        CurNode.Contents.append(sp.AssignType(line))
                        CurNode.Childs.append(node(CurNode, "VAR", idCnt)) #Add Target Child
                        idCnt += 1
                        CurNode.Childs[-1].Contents.append(sp.AssignTarget(line))
                        CurNode.Childs.append(node(CurNode, "RPN", idCnt)) #Add Source Child
                        idCnt += 1
                        rpn = GenRPN(sp.AssignSource(line))
                        CurNode.Childs[-1].Contents.append(rpn)
                        CurNode = rNode

                if type == "WHILE":
                        cond = sp.WhileCondition(line)
                        stack.append(["WHILE", intend])
                        rNode = CurNode
                        CurNode.Childs.append(node(CurNode, "WHILE", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the While node
                        CurNode.Childs.append(node(CurNode, "RPN", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the Condition Child
                        CurNode.Contents.append(GenRPN(cond))
                        CurNode = CurNode.father #Back to While Node
                        CurNode.Childs.append(node(CurNode, "BODY", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the Body Child
                
                if type == "IF":
                        cond = sp.IfCondition(line)
                        stack.append(["IF", intend])
                        rNode = CurNode
                        CurNode.Childs.append(node(CurNode, "IF", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the If Node
                        CurNode.Childs.append(node(CurNode, "RPN", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the Condition Child
                        CurNode.Contents.append(GenRPN(cond))
                        CurNode = CurNode.father #Back to IfNode
                        CurNode.Childs.append(node(CurNode, "BODY", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the Body Child
                
                if type == "ASSREG":
                        rNode = CurNode
                        CurNode.Childs.append(node(CurNode, "ASSREG", idCnt))
                        idCnt += 1
                        CurNode = CurNode.Childs[-1] #Enter the Assreg node
                        CurNode.Childs.append(node(CurNode, "REG", idCnt)) #Add Variable Child
                        idCnt += 1
                        CurNode.Childs[-1].Contents.append(sp.AssReg(line))
                        CurNode.Childs.append(node(CurNode, "VAR", idCnt)) #Add Register Child
                        idCnt += 1
                        CurNode.Childs[-1].Contents.append(sp.AssVar(line))
                        CurNode = rNode
                
                if type == "COMMENT":
                        cnt = sp.CommentContent(line)
                        CurNode.Childs.append(node(CurNode, "COMMENT", idCnt))
                        idCnt += 1
                        CurNode.Childs[-1].Contents.append(cnt)

                if type == "BREAK":
                        CurNode.Childs.append(node(CurNode, "BREAK", idCnt))
                        idCnt += 1

                if type == "CONTINUE":
                        CurNode.Childs.append(node(CurNode, "CONTINUE", idCnt))
                        idCnt += 1





printLevel = 0
def PrintTree(node):
        global printLevel
        for i in range(0, printLevel):
                print(' │ ', sep='', end='')
        if node.id != -1:
                print(" ├──ID: ", node.id, "Father: ", node.father.id, "Type: ", node.type, "Content: ", node.Contents)
        else:
                print(" ├──ID: ", node.id, "Father: ", "None", "Type: ", node.type, "Content: ", node.Contents)
        for i in node.Childs:
                printLevel += 1
                PrintTree(i)
                printLevel -= 1

latexLines = []

def PrintLatex(node):
        global printLevel
        inte = '  '*printLevel
        if node.id != -1:
                latexLines.append("%snode {%d\\\\%s\\\\'%s'}" % (inte, node.id, node.type, str(node.Contents)))
        else:
                latexLines.append("%s\\node {%d\\\\%s\\\\'%s'}" % (inte, node.id, node.type, str(node.Contents)))
        for i in node.Childs:
                latexLines.append("%schild {" % (inte))
                printLevel += 1
                PrintLatex(i)
                printLevel -= 1
                latexLines.append("%s}" % (inte))

def LatexTree(node):
        global latexLines
        global printLevel
        printLevel = 1
        latexLines.append(r"\documentclass[border=20pt]{standalone}")
        latexLines.append(r"\usepackage{tikz}")
        latexLines.append(r"\begin{document}")
        latexLines.append(r"\begin{tikzpicture}[sibling distance=10em, every node/.style = {shape=rectangle, rounded corners, draw, align=center, top color=white, bottom color=white}]]")
        PrintLatex(node)
        latexLines.append(r"\end{tikzpicture}")
        latexLines.append(r"\end{document}")
        return latexLines