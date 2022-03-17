from dis import Instruction
from genericpath import exists
from CacheImplementation import Cache
from CachBlock import Create_Block
import os.path
import sys
import json

class ReadFile:
    
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
    obj_ReadFile = ReadFile
    print("Commands sent through command line" ,n)
    #print(sys.argv[0])
    BLOCKSIZE = int(sys.argv[1])
    L1_SIZE = int(sys.argv[2])
    L1_ASSOC = int(sys.argv[3])
    L2_SIZE = int(sys.argv[4])
    L2_ASSOC = int(sys.argv[5])
    REPLACEMENT_POLICY = int(sys.argv[6])
    if(int(sys.argv[7]) == 0):
        INCLUSION_PROPERTY = "NONINCLUSION"
    else:
        INCLUSION_PROPERTY = "INCLUSION"
    #print(INCLUSION_PROPERTY)
    filePath =sys.argv[8]
    
    L2_Flag = False

    # traceFile1 = [
    #     ['w','0xFA0040E0'],
    #     ['r','0xFF0040E8'],
    #     ['w','0x002183B0'],
    #     ['r','0xFB0040E0'],
    #     ['w','0xBEEF005C'],
    #     ['r','0x00101078'],
    #     ['w','0xFF0040E0'],
    #     ['r','0x00101078'],
    #     ['w','0x002183E0'],
    #     ['w','0x002183D0'],
    #     ['r','0xFE0040E0'],
    #     ['w','0xFF0040E0']
    # ] 

    
    #filePath = r'Traces\gcc_trace.txt'
    #traceFile1 = obj_ReadFile.ReadFile(filePath)
    
    traceFile = obj_ReadFile.ReadFile(filePath)


    # BLOCKSIZE = 16#32
    # L1_SIZE = 1024#256
    # L1_ASSOC = 2
    # L2_SIZE = 0#256
    # L2_ASSOC = 0
    # REPLACEMENT_POLICY = 1
    # INCLUSION_PROPERTY = 'NONINCLUSION'
    # trace_file =traceFile1
    # L2_Flag = False


    if(L2_SIZE > 0 and L2_SIZE != ''):
        L2_Flag = True

    obj_L1Cache = Cache(BLOCKSIZE,L1_SIZE,L1_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,traceFile)

    if(L2_Flag):
        obj_L2Cache = Cache(BLOCKSIZE,L2_SIZE,L2_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,traceFile,L2_Flag)

    if REPLACEMENT_POLICY == 2:
        obj_L1Cache.Create_Tag_OPT(traceFile) #We have opted for OPT replacement policy
        if(L2_Flag):
            obj_L2Cache.Create_Tag_OPT(traceFile)
    
    for i in range(len(traceFile)):
        label_instruc,label_address = traceFile[i].split()
        instruction_returned = obj_L1Cache.ExecuteCache(label_instruc,label_address)
        if instruction_returned == 2:
            #Do not replce the value from l2 unless it is dirty bit
            if(L2_Flag):
                if(obj_L1Cache.IsDirtyBit):
                    obj_L2Cache.ExecuteCache('w',obj_L1Cache.WriteBack_tagaddress)
        if(L2_Flag):
            instruction_returned_l2 = obj_L2Cache.ExecuteCache(label_instruc,label_address)
            if instruction_returned_l2 == 2 and INCLUSION_PROPERTY.upper() == 'INCLUSION':
                obj_L1Cache.SetInvalidBit_l1(label_instruc,obj_L2Cache.WriteBack_tagaddress) 

    obj_L1Cache.CalculateCacheStats()
    if(L2_Flag):
        obj_L2Cache.CalculateCacheStats()

    print(REPLACEMENT_POLICY)
    if(REPLACEMENT_POLICY == 0): 
        replce_policy = "LRU"
    elif(REPLACEMENT_POLICY == 1):
        replce_policy ="Pseudo-LRU"
    elif(REPLACEMENT_POLICY == 2):
        replce_policy ="Optimal"
    print(replce_policy)

    print("----------------------------Simulator Configurations-------------------------------------")
    print("BLOCKSIZE: ",BLOCKSIZE)             
    print("L1_SIZE: ",L1_SIZE)               
    print("L1_ASSOC: ",L1_ASSOC)              
    print("L2_SIZE: ",L2_SIZE)               
    print("L2_ASSOC: ",L2_ASSOC)              
    print("REPLACEMENT POLICY:",replce_policy)    
    print("INCLUSION PROPERTY:",INCLUSION_PROPERTY)    
    print("trace_file:",filePath)            

    print("----------------------------L1 Cache-------------------------------------")
    obj_L1Cache.PrintCache()
    if(L2_Flag):
        print("----------------------------L2 Cache-------------------------------------")
        obj_L2Cache.PrintCache()
    print("----------------------------Cache Stats-------------------------------------")

    

    print('number of L1 reads: ', obj_L1Cache.ReadCount)
    print('number of L1 read misses: ', obj_L1Cache.ReadMissCount)
    print('number of L1 writes: ', obj_L1Cache.WriteCount)
    print('number of L1 write misses: ', obj_L1Cache.WriteMissCount)
    print('L1 miss rate: ', obj_L1Cache.Missrate)
    print('number of L1 writebacks: ', obj_L1Cache.WriteBacksCount)
    if(L2_Flag):
        print('number of L2 reads:  ', str(obj_L1Cache.ReadMissCount + obj_L1Cache.WriteMissCount))
        print('number of L2 read misses ', obj_L2Cache.ReadMissCount)
        print('number of L2 writes:   ', obj_L1Cache.WriteBacksCount)
        print('number of L2 write misses: ', obj_L2Cache.WriteMissCount)
        print('L2 miss rate: ', str(obj_L2Cache.ReadMissCount/(obj_L1Cache.ReadMissCount + obj_L1Cache.WriteMissCount)))
        print('number of L2 writebacks: ', obj_L2Cache.WriteBacksCount)
    else:
        print('number of L2 reads:  ', 0)
        print('number of L2 read misses ', 0)
        print('number of L2 writes:   ', 0)
        print('number of L2 write misses: ', 0)
        print('L2 miss rate: ', 0)
        print('number of L2 writebacks: ', 0)
    if(L2_Flag):
        print('total memory traffic: ', obj_L2Cache.memTraffic)
    else:
        print('total memory traffic: ', obj_L1Cache.memTraffic)


        # label_instruc,label_address = trace_file[i].split()
        # if label_instruc.upper() == 'R':
        #     obj_L1Cache.Read_Cache(label_address)
        # elif(label_instruc.upper() == 'W'):
        #     obj_L1Cache.write_cache(label_address)
        # else:
        #     print('Illegal Instruction')
        # obj_L1Cache.trackIndex_OPT += 1
        #obj_Cache.ExecuteCache(traceFile)
        #obj_Cache.Read_Cache(traceFile)
        #output = obj_Cache.Create_Cache()
        #print(output)


# def ExecuteCache(self, tracefile):

#         if self.replace_policy == 2:
#             self.Create_Tag_OPT(tracefile)
        
#         for i in range(len(tracefile)):
#             label_instruc,label_address = tracefile[i]
#             if label_instruc.upper() == 'R':
#                 self.Read_Cache(label_address)
#             elif label_instruc.upper() == 'W':
#                 self.write_cache(label_address)
#             else:
#                 print('Illegal Instruction')
#             self.trackIndex_OPT += 1
