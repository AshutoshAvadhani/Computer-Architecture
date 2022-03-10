from dis import Instruction
from genericpath import exists
from CacheImplementation import Cache
from CachBlock import Create_Block
import os.path

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

    traceFile = [
        ['w','0xFF0040E0'],
        ['r','0xFF0040E8'],
        ['w','0x002183E0'],
        ['r','0xFF0040E0'],
        ['w','0xBEEF005C'],
        ['r','0x00101078'],
        ['w','0xFF0040E0'],
        ['r','0x00101078'],
        ['w','0x002183E0'],
        ['r','0xFE0040E0'],
        ['w','0xFF0040E0']
    ]   

    obj_ReadFile = ReadFile
    filePath = r'Traces\vortex_trace.txt'
    traceFile1 = obj_ReadFile.ReadFile(filePath)

    BLOCKSIZE = 16
    L1_SIZE = 1024
    L1_ASSOC = 2
    L2_SIZE = 0
    L2_ASSOC = 0
    REPLACEMENT_POLICY = 2
    INCLUSION_PROPERTY = 'NONINCLUSION'
    trace_file =traceFile1
    L2_Flag = False


    if(L2_SIZE > 0 and L2_SIZE != ''):
        L2_Flag = True

    obj_L1Cache = Cache(BLOCKSIZE,L1_SIZE,L1_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,trace_file)

    if(L2_Flag):
        obj_L2Cache = Cache(BLOCKSIZE,L2_SIZE,L2_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,trace_file,L2_Flag)

    if REPLACEMENT_POLICY == 2:
        obj_L1Cache.Create_Tag_OPT(trace_file) #We have opted for OPT replacement policy
        if(L2_Flag):
            obj_L2Cache.Create_Tag_OPT(trace_file)
    
    for i in range(len(trace_file)):
        label_instruc,label_address = trace_file[i].split()
        instruction_returned = obj_L1Cache.ExecuteCache(label_instruc,label_address)

        if instruction_returned == 2:
            #Do not replce the value from l2
            if(L2_Flag):
                if(obj_L1Cache.IsDirtyBit):
                    obj_L2Cache.ExecuteCache('w',obj_L1Cache.WriteBack_tagaddress)
        if(L2_Flag):
            instruction_returned_l2 = obj_L2Cache.ExecuteCache(label_instruc,label_address)
            if instruction_returned_l2 == 2 and INCLUSION_PROPERTY.upper() == 'INCLUSION':
                #print("jhdfkjhfsdkjfdskhjfsdhjkkhjfdshjkdfshkjhjkfdkhjfsdhjkfdhjkfdkhjufsdkhjfdkhj")
                obj_L1Cache.SetInvalidBit_l1(label_instruc,label_address) 

    

    print("----------------------------L1 Cache-------------------------------------")
    obj_L1Cache.PrintCache()
    if(L2_Flag):
        print("----------------------------L2 Cache-------------------------------------")
        obj_L2Cache.PrintCache()

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
