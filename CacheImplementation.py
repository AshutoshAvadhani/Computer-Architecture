from CachBlock import Create_Block

import string
import math


class Cache:

    def __init__(self, BLOCKSIZE, L1_SIZE, L1_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,trace_file):

        self.blocksize = BLOCKSIZE
        self.l1_size = L1_SIZE
        self.l1_assoc = L1_ASSOC
        self.replace_policy = REPLACEMENT_POLICY
        self.Inclusion_prop = INCLUSION_PROPERTY
        self.trace_file = trace_file
        self.l1_set = int(self.l1_size/(self.blocksize * self.l1_assoc))
        self.fileobj = trace_file
        self.Timer = 0       

        self.opt_index = []
        self.opt_tagbits = []
        self.trackIndex_OPT = 0
        
        self.cache = self.Create_Cache()
        print(self.cache)
        
        #self.l2_size = L2_SIZE
        #self.l2_assoc = L2_ASSOC
        #self.obj_block = Create_Block

    ##Create the cache
    def Create_Cache(self):
        cache = []
        for x in range(self.l1_set):
            assoc = []
            for y in range(self.l1_assoc):
                obj_block = Create_Block()
                assoc.append(obj_block)
            cache.append(assoc)

        return cache

    def write_cache(self,label_address):
        
        tag_val,index_val = self.Calculate_Tag_Index_Offset(label_address)
        row_val = self.cache[index_val]
        replacecount = []

        for j in range(len(row_val)):
            if tag_val == self.cache[index_val][j].tagBit:
                self.cache[index_val][j].timeStamp = self.Timer
                self.cache[index_val][j].dirtyBit = True
                self.Timer += 1
                print('Write - hit') 
                break
            elif(self.cache[index_val][j].tagBit == ''):
                self.cache[index_val][j].tagBit = tag_val
                self.cache[index_val][j].timeStamp = self.Timer
                self.cache[index_val][j].dirtyBit = True 
                self.Timer += 1
                print('Write - Miss and then inserted')
                break
            elif(tag_val != self.cache[index_val][j].tagBit):
                replacecount.append(j)
                continue
                
        if(len(replacecount) == self.l1_assoc):
            #here I will call the evict function
            print("Write - Eviction Started")
            self.evict_cache(tag_val,index_val,'W')
            print("Write - Eviction Done")
            pass
        
        self.PrintCache()
    
    def Read_Cache(self, label_address):

        tag_val,index_val = self.Calculate_Tag_Index_Offset(label_address)
        row_val = self.cache[index_val]
        replacecount = []

        #Logic for Hit condtion
        for j in range(len(row_val)):
            if tag_val == self.cache[index_val][j].tagBit:
                self.cache[index_val][j].timeStamp = self.Timer
                self.Timer += 1
                print('Read - hit') 
                break
            elif(self.cache[index_val][j].tagBit == ''):
                self.cache[index_val][j].tagBit = tag_val
                self.cache[index_val][j].timeStamp = self.Timer
                self.Timer += 1
                print('Read - Miss and then inserted')
                break
            elif(tag_val != self.cache[index_val][j].tagBit):
                replacecount.append(j)
                continue
                
        if(len(replacecount) == self.l1_assoc):
            #here I will call the evict function
            print("Read - Eviction Started")
            self.evict_cache(tag_val,index_val,'R')
            print("Read - Eviction Done")
        self.PrintCache()


    def evict_cache(self,TagVal,SetVal,InstructionMode):

        if self.replace_policy == 0:
            self.evict_LRU(SetVal,TagVal,InstructionMode)
            #pass    
        elif self.replace_policy == 1:
            #call for PLRU eviction Policy
            pass
        elif self.replace_policy == 2:
            #call for OPT eviction Policy
            self.evict_OPT(TagVal,SetVal,InstructionMode)
            pass    

    
    #Function for LRU Policy
    def evict_LRU(self, IndexValue, Tag_Address,InstructionMode):
        
        row_val = self.cache[IndexValue]
        min_time_stamp = self.cache[IndexValue][0].timeStamp
        min_index = 0

        for i in range(len(row_val)):
            if min_time_stamp > self.cache[IndexValue][i].timeStamp:
                min_time_stamp = self.cache[IndexValue][i].timeStamp
                min_index = i
        
        self.cache[IndexValue][min_index].tagBit = Tag_Address
        self.cache[IndexValue][min_index].timeStamp = self.Timer
        if(InstructionMode.upper() == 'R'):
            self.cache[IndexValue][min_index].dirtyBit = False
        elif(InstructionMode.upper() == 'W'):
            self.cache[IndexValue][min_index].dirtyBit = True
        self.Timer += 1

    def evict_OPT(self,TagVal,SetVal,InstructionMode):
        
        temp_FutureTag = []
        temp_tagDistance= []
        index_tag = 0
        minDist = 0
        minDist_index = 0
        #First we will get the set from cache for replcing the tag address
        row_val = self.cache[SetVal]

        #We will now split the tag and index array upto the Index being currently used.
        temp_index = self.opt_index[self.trackIndex_OPT+1:]
        temp_tagbits = self.opt_tagbits[self.trackIndex_OPT+1:]

        #Now we have to get the list of all the tag address of the future for that particular set value.
        for i in range(len(temp_tagbits)):
            if(temp_index[i] == SetVal):
                temp_FutureTag.append(temp_tagbits[i])

        #now we will have to check the distance for all the cahce set value and if they are far away then just replce the bit.
        for i in range(len(row_val)):
            temp_cachetag = self.cache[SetVal][i].tagBit
            if temp_cachetag in temp_tagbits:
                index_tag = temp_tagbits.index(temp_cachetag)
            else:
                index_tag = -1
            temp_tagDistance.append((index_tag,temp_cachetag,i))   #here I am storing the previous cache tag value, index in the temp array of tagBits and the Index of the loop
        

        for i in range(len(temp_tagDistance)):
            
            tagdistance = temp_tagDistance[i][0]
            if tagdistance == -1:
                minDist = tagdistance
                minDist_index = temp_tagDistance[i][2]
                break
            else:
                if tagdistance < minDist:
                    minDist = tagdistance
                    minDist_index = temp_tagDistance[i][2]
        
        self.cache[SetVal][minDist_index].tagBit = TagVal
        self.cache[SetVal][minDist_index].timeStamp = self.Timer
        if(InstructionMode.upper() == 'R'):
            self.cache[SetVal][minDist_index].dirtyBit = False
        elif(InstructionMode.upper() == 'W'):
            self.cache[SetVal][minDist_index].dirtyBit = True
        self.Timer += 1
        
    def Calculate_Tag_Index_Offset(self,address):

        #calclulate the address into tag index and ffset bits. return the same.
        #calculate the index bits.
        index_bits = math.log2(self.l1_set)
        #calculate the Offset bits.
        offset_bits = math.log2(self.blocksize)
        #Calculate the Tag bits.
        tag_bits = 32 - (index_bits+offset_bits)  #currently checking only on 32 bits. Afterwards it will be size of address bits.

        binary_address = str(bin(int(address,base=16)))[2:].zfill(32)
        print(binary_address)

        index_val = int(binary_address[int(tag_bits):32-int(offset_bits)],2)
        print(index_val)
        tag="0x"+"{:0{}x}".format(int(binary_address[:int(tag_bits)],2),int(int(tag_bits)/4))
        print(tag)
        #binary_address = Binary(address)
        return tag,index_val

    def PrintCache(self):
        print('==========================================================')
        for i in range(0,self.l1_set):
            print('Set Number -- ' + str(i))
            for j in range(0,self.l1_assoc):
               print("\t"+str(self.cache[i][j].tagBit)+"\t"+str(self.cache[i][j].timeStamp)+"\t"+str(self.cache[i][j].dirtyBit))
        print('==========================================================')
    
    def Create_Tag_OPT(self,traceFile):

        for i in range(len(traceFile)):
            label_instruc,label_address = self.trace_file[i].split()
            tag_val,index_val = self.Calculate_Tag_Index_Offset(label_address)
            self.opt_index.append(index_val)
            self.opt_tagbits.append(tag_val)

