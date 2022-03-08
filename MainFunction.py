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
        ['r','0xFF0040E0'],
        ['r','0xBEEF005C'],
        ['w','0xFF0040E8'],
        ['r','0x00101078'],
        ['r','0xFF0040E0'],
        ['w','0x00101078'],
        ['r','0x002183E0'],
        ['W','0xFE0040E0']
    ]   


    obj_ReadFile = ReadFile

    traceFile = obj_ReadFile.ReadFile('Traces\gcc_trace.txt')

    BLOCKSIZE = 16
    L1_SIZE = 1024
    L1_ASSOC = 2
    L2_SIZE = 0
    L2_ASSOC = 0
    REPLACEMENT_POLICY = 0
    INCLUSION_PROPERTY = 'Inclusion'
    trace_file = traceFile
    L2_Flag = False


    obj_L1Cache = Cache(BLOCKSIZE,L1_SIZE,L1_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,trace_file)

    if(L2_SIZE > 0 and L2_SIZE != ''):
        L2_Flag = True

    if(L2_Flag):
        obj_L2Cache = Cache(BLOCKSIZE,L2_SIZE,L2_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,trace_file)

    if REPLACEMENT_POLICY == 2:
        obj_L1Cache.Create_Tag_OPT(trace_file) #We have opted for OPT replacement policy
        if(L2_Flag):
            obj_L2Cache.Create_Tag_OPT(trace_file)
    
    for i in range(len(trace_file)):
        label_instruc,label_address = trace_file[i].split()
        if label_instruc.upper() == 'R':
            obj_L1Cache.Read_Cache(label_address)
        elif(label_instruc.upper() == 'W'):
            obj_L1Cache.write_cache(label_address)
        else:
            print('Illegal Instruction')
        obj_L1Cache.trackIndex_OPT += 1


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
