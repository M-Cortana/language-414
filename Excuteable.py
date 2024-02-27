import re

regAvailable = ["x1","x2","x3","x4","x5","x6","x7","x8","x9","x10","x11","x12","x13","x14","x15","x16","x17","x18","x19","x20","x21","x22","x23","x24","x25","x26","x27","x28","x29","x30","x31","t0","t1","t2","t3","t4","t5","t6","s0","s1","s2","s3","s4","s5","s6","s7","s8","s9","s10","s11","a0","a1","a2","a3","a4","a5","a6","a7"]

regUsed = []
regDict = {}

def newSysReg():
        i = len(regAvailable) - 1
        while i >= 0:
                if (regAvailable[i] in regUsed) == False:
                        regUsed.append(regAvailable[i])
                        return regAvailable[i]
                i -= 1

def newUsrReg():
        i = 0
        while i < len(regAvailable):
                if (regAvailable[i] in regUsed) == False:
                        regUsed.append(regAvailable[i])
                        return regAvailable[i]
                i += 1

def assReg(inss):
        asss = []
        for i in inss:
                if re.search(r"^ *assign", i) != None:
                        r = re.search(r"(?<=reg\()[a-zA-Z0-9]+(?=\))", i).group()
                        v = re.search(r"(?<=%\()[a-zA-Z0-9]+(?=\))", i).group()
                        regUsed.append(r)
                        regDict[v] = r
                        asss.append(i)
        for j in asss:
                inss.remove(j)

def allocReg(inss):
        for i in inss:
                for v in re.findall(r"(?<=%\()\w+(?=\))", i):
                        if (v in regDict) == False:
                                if (re.search(r"(?<=__)\w+(?=__)", v) != None):
                                        regDict[v] = newSysReg()
                                else:
                                        regDict[v] = newUsrReg()

def printRegTable():
        print("Var              | Reg ")
        print("-----------------------")
        for i in regDict:
                print("%16s | %4s" % (i, regDict[i]))

def replaceVar(inss):
        newinss = []
        for i in inss:
                ni = i
                for v in re.findall(r"(?<=%\()\w+(?=\))", i):
                        ni = re.sub(r"%\("+v+r"\)", regDict[v], ni)
                newinss.append(ni)
        return newinss


def genExcuteable(inss):
        assReg(inss)
        allocReg(inss)
        excuInss = replaceVar(inss)
        return excuInss