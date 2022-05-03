class SmithNBitPredictor:
    def __init__(self,bitSize):

        self.bitSize = bitSize
        self.highBoundry = 0
        self.lowBoundry = 0
        self.threshold = 0
        self.counterSize = 0
        self.misPredictionCount = 0
        self.PredictionCount = 0
        self.SetSmithNBit(self.bitSize)

    def SetSmithNBit(self,bitSize):
        
        self.highBoundry = (2 ** int(bitSize)) -1
        if(int(bitSize) == 2):
            self.counterSize = (int(bitSize)) / 2
        else:
            self.counterSize = (2 ** int(bitSize)) / 2
        self.threshold = (2 ** int(bitSize)) / 2

    def NBitPredict(self):

        if (self.counterSize >= self.threshold):
            Code_prediction = 'T'
        else:
            Code_prediction = 'N'

        return Code_prediction

    def NBitUpdateCounter(self,actualPred):

        if(actualPred.upper() == 'T'):
            if(self.counterSize < self.highBoundry):
                self.counterSize += 1
        else:
            if(self.counterSize > self.lowBoundry):
                self.counterSize -= 1

    def printResult(self):

        print("OUTPUT")
        print("Number of Prediction: ",self.PredictionCount)
        print("Number of Misprediction: ",self.misPredictionCount)
        print("Misprediction Rate: ", round((float(self.misPredictionCount) * 100)/float(self.PredictionCount),2),"%")
        print("Final Counter Values: ",int(self.counterSize))

    def GetCounterValue(self):

        return self.counterSize

class BimodalPredictor:
    def __init__(self,m):
        self.m = m
        self.PredictionTableSize = 2**m
        self.PredictionTable = []
        self.mask = (self.PredictionTableSize -1 )<<2
        for i in range(self.PredictionTableSize):
            objSmithNBit = SmithNBitPredictor(3)
            self.PredictionTable.append(objSmithNBit)
    
    def Predict(self,addressVal,branchPred):

        index = (addressVal & self.mask) >> 2
        Code_prediction = self.PredictionTable[index].NBitPredict()
        return Code_prediction

    def UpdateCounter(self,addressVal,branchPred):
        
        index = (addressVal & self.mask) >> 2
        self.PredictionTable[index].NBitUpdateCounter(branchPred)

    def printResult(self):

        print("Final Bimodal Contents: ")
        for i in range(self.PredictionTableSize):
            print(""+ str(i)+"\t"+str(int(self.PredictionTable[i].GetCounterValue())))

class GSharePredictor:

    def __init__(self,m,n):
        
        self.m = m
        self.n = n
        self.PredictionTableSize = 2**self.m
        self.PredictionTable = []
        self.m_mask = (self.PredictionTableSize-1) << 2
        self.n_mask = 2**(self.n-1)
        self.branchHistoryRegister = 0

        for i in range(self.PredictionTableSize):
            objSmithNBit = SmithNBitPredictor(3)
            self.PredictionTable.append(objSmithNBit)
   
    def Predict(self,addressVal):
        
        lowerMBits = (addressVal & self.m_mask) >> 2
        index = self.branchHistoryRegister ^ lowerMBits
        Code_prediction = self.PredictionTable[index].NBitPredict()
        return Code_prediction

    def updateCounter(self,addressVal,branchPred):

        lowerMBits = (addressVal & self.m_mask) >> 2
        index = self.branchHistoryRegister ^ lowerMBits
        self.PredictionTable[index].NBitUpdateCounter(branchPred)
    
    def updateBrachHistoryRegister(self,branchPred):

        self.branchHistoryRegister = self.branchHistoryRegister>>1
        if(branchPred.upper() == 'T'):
            self.branchHistoryRegister = self.branchHistoryRegister | self.n_mask

    def printResult(self):

        print("Final GShare Contents: ")
        for i in range(self.PredictionTableSize):
            print(""+ str(i)+"\t"+str(int(self.PredictionTable[i].GetCounterValue())))

class HybridBranchPrediction:

    def __init__(self,k,m1,n,m2):

        self.PredictionTableSize = 2**k
        self.PredictionTable = []
        for i in range(self.PredictionTableSize):
            objSmithNBit = SmithNBitPredictor(2)
            self.PredictionTable.append(objSmithNBit)

        self.obj_BimodalPred = BimodalPredictor(m2)
        self.obj_GSharePred = GSharePredictor(m1,n)
        self.Kmask = (self.PredictionTableSize-1) << 2
        self.PredictionCount = 0
        self.misPredictionCount = 0

    def HybridBranchPredict(self,addressVal,branchVal):

        self.PredictionCount = len(branchVal)

        for i in range(self.PredictionCount):
            bimodalPred = self.obj_BimodalPred.Predict(addressVal[i],branchVal[i])
            GSharePred = self.obj_GSharePred.Predict(addressVal[i])

            lowerbit = (addressVal[i] & self.Kmask) >> 2
            Chooser_pred = self.PredictionTable[lowerbit].NBitPredict()

            if(Chooser_pred.upper() == "T" ):
                final_pred = GSharePred
                self.obj_GSharePred.updateCounter(addressVal[i],branchVal[i])
            else:
                final_pred = bimodalPred
                self.obj_BimodalPred.UpdateCounter(addressVal[i],branchVal[i])

            self.obj_GSharePred.updateBrachHistoryRegister(branchVal[i]) #Branch History register will be updated every time 
            
            if(bimodalPred.upper() == branchVal[i].upper() and GSharePred.upper() != branchVal[i].upper()):
                self.PredictionTable[lowerbit].NBitUpdateCounter('N')
            elif(bimodalPred.upper() != branchVal[i].upper() and GSharePred.upper() == branchVal[i].upper()):
                self.PredictionTable[lowerbit].NBitUpdateCounter('T')
            
            if(final_pred.upper() != branchVal[i].upper()):
                self.misPredictionCount += 1

        self.printResult()
        self.obj_GSharePred.printResult()
        self.obj_BimodalPred.printResult()

    def printResult(self):
        
        print("OUTPUT")
        print("Number of Prediction: ",self.PredictionCount)
        print("Number of Misprediction: ",self.misPredictionCount)
        print("Misprediction Rate: ", round((float(self.misPredictionCount) * 100)/float(self.PredictionCount),2),"%")
        
        print("Final Chooser Contents: ")
        for i in range(self.PredictionTableSize):
            print(""+ str(i)+"\t"+str(int(self.PredictionTable[i].GetCounterValue())))