import os.path
import sys
from TomasuloAlgo import TomasuloAlgorithm

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
    n = len(sys.argv)
    print("Commands sent through command line" ,n)

    SchedulingQueueSize = str(sys.argv[2]).upper()
    PeakFetchDispatchRate = str(sys.argv[3]).upper()
    traceFileName = str(sys.argv[4])

    obj_ReadFile = ReadFile
    traceFile = obj_ReadFile.ReadFile(traceFileName)

    objTomasulo = TomasuloAlgorithm(SchedulingQueueSize,PeakFetchDispatchRate)
    objTomasulo.dynamicscheduling(traceFile)




