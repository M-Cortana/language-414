import SyntaxTree as st
import Assemble as ab
import Excuteable as ec
import re
srcFileName = input("Source File Name: ")
srcFile = open(srcFileName, mode = "r")
srcLines = srcFile.readlines()
st.ConstructSyntaxTree(srcLines)
print("\n\nSyntax Tree:")
st.PrintTree(st.root)
ab.ParseSyntaxTree(st.root)

eci = ec.genExcuteable(ab.Instructions)

print("\n\nRegister Table: ")
ec.printRegTable()

if re.search(r".*(?=.414)", srcFileName) != None:
        outFileName = re.search(r".*(?=.414)", srcFileName).group() + ".out"
else:
        outFileName = srcFileName + ".out"
outFile = open(outFileName, mode = "w")
for i in eci:
        print(i, file = outFile)
