import os.path
import sys
from BranchPrediction import branchPrediction

class ReadFile:
    #read the trace file 
    def ReadFile(filename):
        file_exists = os.path.exists(filename)
        tracefile = []
        if(file_exists):
            fileobj = open(filename,"r",encoding='utf-8-sig') 
            for line in fileobj.readlines():
                if line == "\n":
                    continue
                else:
                    tracefile.append(line.rstrip())
        return tracefile


if __name__ == '__main__':
    
    branchPred = [] #for saving the Actual Branch Prediction 
    addressVal = [] #For storing the converted Addresses 

    n = len(sys.argv)
    #print("Commands sent through command line" ,n)

    BranchPredictorType = str(sys.argv[1]).upper()
    bitSize = 0
    k=0
    m2 = 0
    m1 = 0
    n = 0

    cmdStr = "./sim "+str(BranchPredictorType)

    if BranchPredictorType == "SMITH":
        bitSize = int(sys.argv[2])
        TraceFileName = str(sys.argv[3])
        cmdStr = cmdStr + " " + str(bitSize)+" " +str(TraceFileName)
    elif BranchPredictorType == "BIMODAL":
        m2 = int(sys.argv[2])
        TraceFileName = str(sys.argv[3])
        cmdStr = cmdStr + " " + str(m2)+" " +str(TraceFileName)
    elif BranchPredictorType == "GSHARE":
        m1 = int(sys.argv[2])
        n = int(sys.argv[3])
        TraceFileName = str(sys.argv[4])
        cmdStr = cmdStr + " " + str(m1)+" "+str(n)+ " " +str(TraceFileName)
    elif BranchPredictorType == "HYBRID":
        k = int(sys.argv[2])
        m1 = int(sys.argv[3])
        n = int(sys.argv[4])
        m2 = int(sys.argv[5])
        TraceFileName = str(sys.argv[6])
        cmdStr = cmdStr + " " + str(k)+" "+str(m1)+ " "+str(n)+" "+str(m2)+" " +str(TraceFileName)

    obj_ReadFile = ReadFile
    traceFile = obj_ReadFile.ReadFile(TraceFileName)
    
    obj_BranchPred = branchPrediction(BranchPredictorType,bitSize,m2,m1,n,TraceFileName,k)

    if(len(traceFile) > 0):
        for i in range(len(traceFile)):
            branchInstr,predBranch = traceFile[i].split()
            branchInstr = int(branchInstr,16)
            addressVal.append(branchInstr)
            branchPred.append(predBranch)
        print("COMMAND")
        print(cmdStr)
        obj_BranchPred.BranchPrediction(addressVal,branchPred)