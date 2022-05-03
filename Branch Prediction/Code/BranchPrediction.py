from HybridPrediction import HybridBranchPrediction

class BimodalPredictor:
    
    def __init__(self,m):

        self.m = m
        self.PredictionTableSize = 2**m
        self.PredictionTable = []
        self.PredictionCount = 0
        self.misPredictionCount = 0
        self.mask = (self.PredictionTableSize -1 )<<2
        for i in range(self.PredictionTableSize):
            objSmithNBit = SmithNBitPredictor(3)
            self.PredictionTable.append(objSmithNBit)
    
    def Predict(self,addressVal,branchPred):
        
        index = (addressVal & self.mask) >> 2
        Code_prediction = self.PredictionTable[index].SmithNBit_Predict(branchPred)
        return Code_prediction

    def BimodalBranchPredictor(self,address,branchVal):

        self.PredictionCount = len(branchVal)
        for i in range(self.PredictionCount):
            codePrediction = self.Predict(address[i],branchVal[i])
            if(codePrediction.upper() != branchVal[i].upper()):
                self.misPredictionCount +=  1
        self.printResult()
        
    def printResult(self):
        
        print("OUTPUT")
        print("Number of Prediction: ",self.PredictionCount)
        print("Number of Misprediction: ",self.misPredictionCount)
        print("Misprediction Rate: ", round((float(self.misPredictionCount) * 100)/float(self.PredictionCount),2),"%")
        
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
        self.PredictionCount = 0
        self.misPredictionCount = 0
        self.branchHistoryRegister = 0

        for i in range(self.PredictionTableSize):
            objSmithNBit = SmithNBitPredictor(3)
            self.PredictionTable.append(objSmithNBit)

    def Predict(self,addressVal,branchPred):

        lowerMBits = (addressVal & self.m_mask) >> 2
        index = self.branchHistoryRegister ^ lowerMBits
        Code_prediction = self.PredictionTable[index].SmithNBit_Predict(branchPred)
        self.branchHistoryRegister = self.branchHistoryRegister>>1
        if(branchPred.upper() == 'T'):
            self.branchHistoryRegister = self.branchHistoryRegister | self.n_mask
        return Code_prediction
    
    def GShareBranchPredictor(self,address,branchVal):

        self.PredictionCount = len(branchVal)
        for i in range(self.PredictionCount):
            codePrediction = self.Predict(address[i],branchVal[i])
            if(codePrediction.upper() != branchVal[i].upper()):
                self.misPredictionCount +=  1
        self.printResult()

    def printResult(self):
        
        print("OUTPUT")
        print("Number of Prediction: ",self.PredictionCount)
        print("Number of Misprediction: ",self.misPredictionCount)
        print("Misprediction Rate: ", round((float(self.misPredictionCount) * 100)/float(self.PredictionCount),2),"%")
        
        print("Final GShare Contents: ")
        for i in range(self.PredictionTableSize):
            print(""+ str(i)+"\t"+str(int(self.PredictionTable[i].GetCounterValue())))

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
        self.counterSize = (2 ** int(bitSize)) / 2
        self.threshold = (2 ** int(bitSize)) / 2

    def SmithNBit_Predict(self,actualPred):
        
        if (self.counterSize >= self.threshold):
            Code_prediction = 'T'
        else:
            Code_prediction = 'N'
    
        if(actualPred.upper() == 'T'):
            if(self.counterSize < self.highBoundry):
                self.counterSize += 1
        else:
            if(self.counterSize > self.lowBoundry):
                self.counterSize -= 1
        
        return Code_prediction

    def SmithNBitBranchPredictor(self,branchPred):

        self.PredictionCount = len(branchPred)
        for i in range(self.PredictionCount):
            codePrediction = self.SmithNBit_Predict(branchPred[i])
            if(codePrediction.upper() != branchPred[i].upper()):
                self.misPredictionCount +=  1
        self.printResult()

    def printResult(self):

        print("OUTPUT")
        print("Number of Prediction: ",self.PredictionCount)
        print("Number of Misprediction: ",self.misPredictionCount)
        print("Misprediction Rate: ", round((float(self.misPredictionCount) * 100)/float(self.PredictionCount),2),"%")
        print("Final Counter Values: ",int(self.counterSize))

    def GetCounterValue(self):
        return self.counterSize

class branchPrediction:

    def __init__(self,PredictorType,bitSize,m2,m1,n,TraceFileName,k):
        
        self.predictorType = PredictorType
        self.bitSize = bitSize
        self.m2 = m2
        self.m1 = m1
        self.n = n
        self.k = k
        self.tracefileName = TraceFileName
    
    def BranchPrediction(self,addressVal,branchPred):

        if self.predictorType.upper() == "SMITH":
            objSmith = SmithNBitPredictor(self.bitSize)
            objSmith.SmithNBitBranchPredictor(branchPred)
        elif self.predictorType.upper() == "BIMODAL":
            objBimodal = BimodalPredictor(self.m2)
            objBimodal.BimodalBranchPredictor(addressVal,branchPred)
        elif self.predictorType.upper() == "GSHARE":
            objGShare = GSharePredictor(self.m1,self.n)
            objGShare.GShareBranchPredictor(addressVal,branchPred)
        elif self.predictorType.upper() == "HYBRID":
            objHybrid = HybridBranchPrediction(self.k,self.m1,self.n,self.m2)
            objHybrid.HybridBranchPredict(addressVal,branchPred)
    
                
