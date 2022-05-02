from InstructionObject import Instruction

class TomasuloAlgorithm:

    def __init__(self,SchedulingQueueSize,PeakFetchDispatchRate):
        
        self.CurrentCycle = 0
        self.operationCount = 0
        
        #list to contain all the objects of Instruction class
        self.lst_Instruction = []
        #list to contain all the instructions which are completed.
        self.lst_Completed = []
        
        #lists for instruction to remain in.
        # Dispatch List ==>  This contains a list of instructions in either the IF or ID state. The dispatch_list models the Dispatch Queue.
        self.lst_Dispatch = []
        # Issue List ==> This contains a list of instructions in the IS state.
        self.lst_Issue = []
        #Execute List = This contains a list of instructions in the EX state
        self.lst_evaluate = []

        #Reorder Buffer
        self.lst_ReorderBuff = []
        
        #States for instructions to be in.
        self.IF_fetch = 0
        self.ID_dispatch = 0

        self.SchedulingQueueSize = SchedulingQueueSize
        self.PeakFetchDispatchRate = PeakFetchDispatchRate

    def FileOperation(self, traceFile):
        temp = []
        if(len(traceFile) > 0):
            for i in range(len(traceFile)):
                temp = traceFile[i].split()

                objinstr = Instruction()
                objinstr.programCounter = temp[0]   
                objinstr.OperationType = temp[1]    
                objinstr.destinationReg = temp[2]   
                objinstr.sourceReg1 = temp[3]   
                objinstr.sourceReg2 =  temp[4]  
                objinstr.tagCount = i

                self.lst_Instruction.append(objinstr)
                self.lst_ReorderBuff.append(objinstr)
                self.operationCount += 1

    def printResult(self):
        lst_temp = []
        lst_temp = self.lst_Completed

        for i in range(len(self.lst_ReorderBuff)):
            for j in range(len(lst_temp)):
                if(self.lst_ReorderBuff[i].programCounter == lst_temp[j].programCounter):
                    temp = []
                    temp = lst_temp[j]
                    self.lst_ReorderBuff[i] = temp
                    lst_temp.pop(j)
                    break

        for i in range(len(self.lst_ReorderBuff)):
            print(str(i) + " fu{" +str(self.lst_ReorderBuff[i].OperationType) + "} src{" + str(self.lst_ReorderBuff[i].sourceReg1 + "," + self.lst_ReorderBuff[i].sourceReg2) + "} dst{" + str(self.lst_ReorderBuff[i].destinationReg) + "} IF{" + str(self.lst_ReorderBuff[i].CurrentCycle) + "," + str(int(self.lst_ReorderBuff[i].Cycle) - int(self.lst_ReorderBuff[i].CurrentCycle)) + "} ID{" + str(int(self.lst_ReorderBuff[i].Cycle)) + "," + str(int(self.lst_ReorderBuff[i].IssueCycleCount) - int(self.lst_ReorderBuff[i].Cycle)) + "} IS{" + str(int(self.lst_ReorderBuff[i].IssueCycleCount)) + "," + str(int(self.lst_ReorderBuff[i].ExecuteCycleCount) -int(self.lst_ReorderBuff[i].IssueCycleCount)) +"} EX{" + str(int(self.lst_ReorderBuff[i].ExecuteCycleCount)) +"," + str(int(self.lst_ReorderBuff[i].LastCycleCount)-int(self.lst_ReorderBuff[i].ExecuteCycleCount)) + "} WB{" + str(int(self.lst_ReorderBuff[i].LastCycleCount)) + ",1}")

        print("Number of Instructions: ",self.operationCount)
        print("Number of cycles: ",self.CurrentCycle)
        print("IPC: ", round(float(self.operationCount)/float(self.CurrentCycle),5))

    def dynamicscheduling(self,traceFile):
        
        self.FileOperation(traceFile)

        while(len(self.lst_Completed) < self.operationCount):
            
            #last Step
            a = 0
            while(a < len(self.lst_evaluate)):
                CompletedLatency = 1
                if(int(self.lst_evaluate[a].OperationType) == 1):
                    CompletedLatency = 2
                elif(int(self.lst_evaluate[a].OperationType) == 2):
                    CompletedLatency = 5
                if(int(self.lst_evaluate[a].ExecuteCycleCount) + CompletedLatency <= self.CurrentCycle):
                    temp = []
                    temp = self.lst_evaluate[a]
                    if(temp.LastCycleCount == ""):
                        temp.LastCycleCount = str(int(self.CurrentCycle))
                    self.lst_Completed.append(temp)
                    self.lst_evaluate.pop(a)
                    a -= 1 #To always keep the counter at the start of the list
                a += 1    

            #EX State
            i=0
            while(i < len(self.lst_Issue)):
                skip = False
                if(len(self.lst_evaluate) <= int(self.PeakFetchDispatchRate) + 1):
                    if(i > 0):
                        p = 0
                        while(p < i):
                            if(((self.lst_Issue[i].sourceReg1 == self.lst_Issue[p].destinationReg) and (int(self.lst_Issue[p].destinationReg) != -1)) or ((self.lst_Issue[i].sourceReg2 == self.lst_Issue[p].destinationReg) and (int(self.lst_Issue[p].destinationReg) != -1))):
                                skip = True
                                break
                            p += 1
                    if(len(self.lst_evaluate) > 0):
                        newEntry = []
                        newEntry = self.lst_Issue[i]
                        hasDep = False
                        e = len(self.lst_evaluate) - 1
                        while(e >= 0):
                            if(((self.lst_Issue[i].sourceReg1 == self.lst_evaluate[e].destinationReg) or (self.lst_Issue[i].sourceReg2 == self.lst_evaluate[e].destinationReg))and (int(self.lst_evaluate[e].destinationReg) != -1)):
                                if((int(self.lst_evaluate[e].tagCount) < int(self.lst_Issue[i].tagCount)) and (int(newEntry.tagCount) == int(self.lst_Issue[i].tagCount))):
                                    newEntry = self.lst_evaluate[e]
                                    hasDep = True
                                if((int(newEntry.tagCount) != int(self.lst_Issue[i].tagCount)) and (int(self.lst_evaluate[e].tagCount) > int(newEntry.tagCount)) and (int(self.lst_evaluate[e].tagCount) < int(self.lst_Issue[i].tagCount))):
                                    newEntry = self.lst_evaluate[e]
                            e -= 1
                        c = len(self.lst_Completed) - 1
                        while(c >= 0):
                            if((self.lst_Completed[c].destinationReg == newEntry.destinationReg) and (int(self.lst_Completed[c].tagCount) > int(newEntry.tagCount)) and (int(self.lst_Completed[c].tagCount) < int(self.lst_Issue[i].tagCount))):
                                hasDep = False
                                break
                            c -= 1
                        if(hasDep):
                            latency = 1 #default latency is 1
                            if(int(newEntry.OperationType) == 1):
                                latency = 2
                            elif(int(newEntry.OperationType) == 2):
                                latency = 5
                            if(int(newEntry.ExecuteCycleCount) + latency + 1 > self.CurrentCycle):
                                skip = True
                    if(skip):
                        pass
                    else:
                        temp = []
                        temp = self.lst_Issue[i]
                        if(self.lst_Issue[i].ExecuteCycleCount == ""):
                            temp.ExecuteCycleCount = str(int(self.CurrentCycle))
                        self.lst_evaluate.append(temp)
                        self.lst_Issue.pop(i)
                        i -= 1
                i += 1

            #IN IS and ID state we do the following operations:-
                #Remove the instruction from the dispatch_list and add it to the issue_list.
                #Reserve a schedule queue entry and free a dispatch queue entry.
                #Transition from the ID state to the IS state.
            #IS State
            i = 0
            while(i < len(self.lst_Dispatch)):
                if(self.lst_Dispatch[i].Cycle != "" and (len(self.lst_Issue) < int(self.SchedulingQueueSize))):
                    temp = []
                    temp = self.lst_Dispatch[i]
                    if(self.lst_Dispatch[i].IssueCycleCount == ""):
                        temp.IssueCycleCount = str(int(self.CurrentCycle))
                    self.lst_Issue.append(temp)
                    self.lst_Dispatch.pop(i)
                    i -= 1
                i += 1

            #ID State
            for i in range(len(self.lst_Dispatch)):
                if((int(self.lst_Dispatch[i].CurrentCycle) == (self.CurrentCycle - 1)) and self.lst_Dispatch[i].Cycle == ""):
                    temp = []
                    temp = self.lst_Dispatch[i]
                    temp.Cycle = str(int(self.CurrentCycle))
                    self.IF_fetch -= 1
                    self.ID_dispatch += 1

            #IF State
            # you have not reached the end-of-file  #fetch bandwidth is not exceeded # the dispatch queue is not full
            while((len(self.lst_Dispatch) < (int(self.PeakFetchDispatchRate) * 2)) and (len(self.lst_Instruction) > 0) and (self.IF_fetch < int(self.PeakFetchDispatchRate))):
                #Read new instructions from the trace 
                temp = []
                temp = self.lst_Instruction[0]
                temp.CurrentCycle = str(int(self.CurrentCycle))
                #Add the instruction to the dispatch_list and reserve a dispatch queue entry
                self.lst_Dispatch.append(temp)
                self.lst_Instruction.pop(0)
                self.IF_fetch += 1

            self.CurrentCycle += 1

        self.printResult()