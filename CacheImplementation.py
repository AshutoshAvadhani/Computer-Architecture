from cProfile import label
from cmath import inf
from platform import node
from select import select
from CachBlock import Create_Block
from CachBlock import PLRUNode
import string
import math

class Cache:
    
    def __init__(self, BLOCKSIZE, L1_SIZE, L1_ASSOC,REPLACEMENT_POLICY,INCLUSION_PROPERTY,trace_file,L2_Flag = False):

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
        self.IsDirtyBit = False

        self.cache = self.Create_Cache()

        self.L2_Flag= L2_Flag

        #both value will be required for changing the l1 cache Writeback policy
        self.OldTag_Index = 0
        self.OldTag_Inclusion = '' 

        #both value will be required for changing the L2 cache Writeback policy
        self.WriteBack_l2 = False
        self.Writeback_IndexValue = 0

        self.WriteBack_tagaddress = ''
        self.WriteBack_tagValue = ''

        self.ReadCount = 0
        self.ReadMissCount = 0
        self.WriteCount = 0
        self.WriteMissCount = 0
        self.Missrate = 0
        self.WriteBacksCount = 0
        self.memTraffic = 0

    def ExecuteCache(self,label_instruc,label_address):
        if label_instruc.upper() == 'R':
            self.ReadCount += 1
            instruction_result = self.Read_Cache(label_address)
        elif(label_instruc.upper() == 'W'):
            self.WriteCount += 1
            instruction_result = self.write_cache(label_address)
        else:
            print('Illegal Instruction')
        self.trackIndex_OPT += 1
        instruction = instruction_result
        return instruction

    ##Create the cache
    def Create_Cache(self):
        cache = []
        for x in range(self.l1_set):
            
            if self.replace_policy == 1:
                assoc = self.CreatePLRUTree(int(math.log2(self.l1_assoc)))
            else:
                assoc = []
                for y in range(self.l1_assoc):
                    obj_block = Create_Block()
                    assoc.append(obj_block)
            cache.append(assoc)

        return cache

    def CreatePLRUTree(self,treeHeight):
        root = PLRUNode()
        stack = [root]
        
        for i in range(treeHeight):
            for j in range(2**i):
                tempNode = stack.pop(0) 
                leftNode = PLRUNode()
                rightNode = PLRUNode()
                tempNode.left = leftNode
                tempNode.right = rightNode
                stack.extend([leftNode, rightNode])
        self.FillPLRUTree(root)
        return root


    def FillPLRUTree(self,root):
        stack = [root]
        while stack:
            node = stack.pop(0)
            if node.left is None and node.right is None:
                cacheblock = Create_Block()
                node.block = cacheblock
                continue
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)

    def Read_Cache(self, label_address):
        tag_val,index_val = self.Calculate_Tag_Index_Offset(label_address)
        row_val = self.cache[index_val]
        replacecount = []
        result = -inf  ## we will set reult as 0 = hit, 1=Miss and Insert, 2= Miss and replace

        if self.replace_policy == 1:
            #Call readFunction fopr RLU
            result = self.Read_Cache_PLRU(tag_val,index_val,label_address)
        else:
            #Logic for Hit condtion
            for j in range(len(row_val)):
                #logic for changing the invalid bit in l1 cache when it has been set to invalid 
                if(self.L2_Flag == False and self.Inclusion_prop.upper() == 'INCLUSION'):
                    if(self.cache[index_val][j].IsValidBit == False):
                        self.cache[index_val][j].tagBit = tag_val
                        self.cache[index_val][j].TagAddress = label_address
                        self.cache[index_val][j].timeStamp = self.Timer
                        self.cache[index_val][j].IsValidBit = True
                        self.Timer += 1
                        #self.ReadMissCount +=1
                        result = 1
                        break
                if tag_val == self.cache[index_val][j].tagBit:
                    self.cache[index_val][j].timeStamp = self.Timer
                    self.cache[index_val][j].TagAddress = label_address
                    self.Timer += 1
                    #print('Read - hit') 
                    result = 0    
                    break
                elif(self.cache[index_val][j].tagBit == ''):
                    self.cache[index_val][j].tagBit = tag_val
                    self.cache[index_val][j].TagAddress = label_address
                    self.cache[index_val][j].timeStamp = self.Timer
                    self.cache[index_val][j].IsValidBit = True
                    self.Timer += 1
                    #print('Read - Miss and then inserted')
                    self.ReadMissCount +=1
                    result = 1
                    break
                elif(tag_val != self.cache[index_val][j].tagBit):
                    replacecount.append(j)
                    continue     
            if(len(replacecount) == self.l1_assoc):
                #here I will call the evict function
                #print("Read - Eviction Started")
                self.evict_cache(tag_val,index_val,'R',label_address)
                self.ReadMissCount += 1
                result = 2
                #print("Read - Eviction Done")
            #self.PrintCache()
        return result

    def write_cache(self,label_address):
        tag_val,index_val = self.Calculate_Tag_Index_Offset(label_address)
        row_val = self.cache[index_val]
        replacecount = []
        result = -inf   #0 for hit, 1 = Miss and insert , 2 = Miss and Replace

        if self.replace_policy == 1:
            #Call readFunction fopr RLU
            result = self.Write_Cache_PLRU(tag_val,index_val,label_address)
        else:
            for j in range(len(row_val)):
                if(self.L2_Flag == False and self.Inclusion_prop.upper() == 'INCLUSION'):
                    if(self.cache[index_val][j].IsValidBit == False):
                        self.cache[index_val][j].tagBit = tag_val
                        self.cache[index_val][j].TagAddress = label_address
                        self.cache[index_val][j].timeStamp = self.Timer
                        self.cache[index_val][j].IsValidBit = True
                        self.cache[index_val][j].dirtyBit = True 
                        self.Timer += 1
                        #self.ReadMissCount +=1
                        result = 1
                        break
                if tag_val == self.cache[index_val][j].tagBit:
                    self.cache[index_val][j].timeStamp = self.Timer
                    self.cache[index_val][j].dirtyBit = True
                    self.cache[index_val][j].TagAddress = label_address
                    self.Timer += 1  
                    #print('Write - hit') 
                    result = 0
                    break
                elif(self.cache[index_val][j].tagBit == ''):
                    self.cache[index_val][j].tagBit = tag_val
                    self.cache[index_val][j].timeStamp = self.Timer
                    self.cache[index_val][j].dirtyBit = True 
                    self.cache[index_val][j].TagAddress = label_address
                    self.cache[index_val][j].IsValidBit = True
                    self.Timer += 1
                    self.WriteMissCount += 1
                    #print('Write - Miss and then inserted')
                    result = 1
                    break
                elif(tag_val != self.cache[index_val][j].tagBit):
                    replacecount.append(j)
                    continue
                    
            if(len(replacecount) == self.l1_assoc):
                #here I will call the evict function
                #print("Write - Eviction Started")
                self.evict_cache(tag_val,index_val,'W',label_address)
                self.WriteMissCount += 1
                result = 2
                #print("Write - Eviction Done")
        #self.PrintCache()
        return result

    def Read_Cache_PLRU(self,tag_val,index_val,label_address):
        
        row_val = self.cache[index_val]
        miss_replace = 0
        #first we will check if the tagvalue is present in the cache block or not.

        s1 = [] #will help in saving the path
        s2 = [] #will contain the leaf node array

        s1.append(row_val)

        while (len(s1)!= 0):
            curr_node = s1.pop()
            if curr_node.left:
                s1.append(curr_node.left)
            if curr_node.right:
                s1.append(curr_node.right)
            if not curr_node.left and not curr_node.right:
                s2.append(curr_node)

        for i in range(len(s2)):
            if (tag_val == s2[i].block.tagBit):
                #Here I will add the condition for hit
                if(self.PLRU_Hit(self.cache[index_val],tag_val,'Read')):
                    return 0

        for i in range(len(s2)):
            if(s2[i].block.tagBit == ''):
                 #this will be the condition for miss insert tagvalue
                self.UpdateTree(self.cache[index_val],tag_val,label_address,'read','r',False)
                self.ReadMissCount += 1
                return 1           
            else:
                miss_replace += 1

        if(miss_replace == len(s2)):
            #We will call the evict function 
            self.evict_cache(tag_val,index_val,'R',label_address)
            self.ReadMissCount += 1
            return 2

    def Write_Cache_PLRU(self,tag_val,index_val,label_address):
        
        row_val = self.cache[index_val]
        counter_miss = 0
        miss_replace = 0
        #first we will check if the tagvalue is present in the cache block or not.

        s1 = [] #will help in saving the path
        s2 = [] #will contain the leaf node array
        s1.append(row_val)

        while (len(s1)!= 0):
            curr_node = s1.pop()
            if curr_node.left:
                s1.append(curr_node.left)
            if curr_node.right:
                s1.append(curr_node.right)
            if not curr_node.left and not curr_node.right:
                s2.append(curr_node)

        for i in range(len(s2)):
            if (tag_val == s2[i].block.tagBit):
                #Here I will add the condition for hit
                if(self.PLRU_Hit(self.cache[index_val],tag_val,'Write')):
                    return 0
            
        for i in range(len(s2)):
            if(s2[i].block.tagBit == ''):
                 #this will be the condition for miss insert tagvalue
                self.UpdateTree(self.cache[index_val],tag_val,label_address,'Write','r',True)
                self.WriteMissCount += 1
                return 1
                #counter_miss += 1            
            else:
                miss_replace += 1

        if(miss_replace == len(s2)):
            #We will call the evict function 
            self.evict_cache(tag_val,index_val,'W',label_address)
            self.WriteMissCount += 1
            return 2   

    def evict_cache(self,TagVal,SetVal,InstructionMode,label_address):
        if self.replace_policy == 0:
            self.evict_LRU(SetVal,TagVal,InstructionMode,label_address)
            #pass    
        elif self.replace_policy == 1:
            #call for PLRU eviction Policy
            self.Evict_PLRU(SetVal,TagVal,InstructionMode,label_address)
            #pass
        elif self.replace_policy == 2:
            #call for OPT eviction Policy
            self.evict_OPT(TagVal,SetVal,InstructionMode,label_address)
            #pass    
    
    def Evict_PLRU(self, IndexValue, Tag_Address,InstructionMode,label_address):
        self.UpdateTree(self.cache[IndexValue],Tag_Address,label_address,InstructionMode,'r',True)
    
    #Function for LRU Policy
    def evict_LRU(self, IndexValue, Tag_Address,InstructionMode,label_address):
        
        row_val = self.cache[IndexValue]
        min_time_stamp = self.cache[IndexValue][0].timeStamp
        min_index = 0

        for i in range(len(row_val)):
            # we are adding the condition here for checking if the block is invalid or not.
            if (self.L2_Flag == False):
                if self.cache[IndexValue][i].IsValidBit == False:
                    min_index = i
                    break
            if min_time_stamp > self.cache[IndexValue][i].timeStamp:
                min_time_stamp = self.cache[IndexValue][i].timeStamp
                min_index = i
        
        #####
        ##for values where we are evicting only the dirty bit to L2 and insert the dirty bit into L2 cache
        if (self.L2_Flag == False):
            if self.cache[IndexValue][min_index].dirtyBit == True:
                self.WriteBacksCount += 1
                self.WriteBack_tagValue = self.cache[IndexValue][min_index].tagBit
                self.WriteBack_tagaddress = self.cache[IndexValue][min_index].TagAddress   #this will help in storing the tag value and the main adress tag for l2 cache
                self.IsDirtyBit = True
            else:
                self.IsDirtyBit = False #this will happen when l1 cache evict is happening but l2 writeback will not happen(DirtyBit == true)
                #print("Writeback Address -- " , self.WriteBack_tagaddress)
        
        #This condition will help in making value of tagbit in l1 as invalid
        if(self.L2_Flag == True):
            if(self.cache[IndexValue][min_index].dirtyBit == True):
                self.WriteBacksCount += 1
            if(self.Inclusion_prop.upper() == "INCLUSION"):
                self.WriteBack_tagValue = self.cache[IndexValue][min_index].tagBit
                self.WriteBack_tagaddress = self.cache[IndexValue][min_index].TagAddress   #this will help in storing the tag value and the main adress tag for l1 cache

        self.cache[IndexValue][min_index].tagBit = Tag_Address
        self.cache[IndexValue][min_index].timeStamp = self.Timer
        self.cache[IndexValue][min_index].TagAddress = label_address
        if(InstructionMode.upper() == 'R'):
            self.cache[IndexValue][min_index].dirtyBit = False
        elif(InstructionMode.upper() == 'W'):
            self.cache[IndexValue][min_index].dirtyBit = True
        self.Timer += 1

    def evict_OPT(self,TagVal,SetVal,InstructionMode,label_address):
        
        temp_FutureTag = []
        temp_tagDistance= []
        index_tag = 0
        maxDist = 0
        maxDist_index = 0
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
            if temp_cachetag in temp_FutureTag:
                index_tag = temp_FutureTag.index(temp_cachetag)
            else:
                index_tag = -1
            temp_tagDistance.append((index_tag,temp_cachetag,i))   #here I am storing the previous cache tag value, index in the temp array of tagBits and the Index of the loop
        
        for i in range(len(temp_tagDistance)):
            tagdistance = temp_tagDistance[i][0]
            if tagdistance == -1:
                maxDist = tagdistance
                maxDist_index = temp_tagDistance[i][2]
                break
            else:
                if tagdistance > maxDist:
                    maxDist = tagdistance
                    maxDist_index = temp_tagDistance[i][2]
        
        if (self.L2_Flag == False): #for l1 writebacks
            if self.cache[SetVal][maxDist_index].dirtyBit == True:
                self.WriteBacksCount += 1
        
        if(self.L2_Flag == True):  #for l2 writebacks
            if(self.cache[SetVal][maxDist_index].IsDirtyBit == True):
                self.WriteBacksCount += 1

        self.cache[SetVal][maxDist_index].tagBit = TagVal
        self.cache[SetVal][maxDist_index].timeStamp = self.Timer
        if(InstructionMode.upper() == 'R'):
            self.cache[SetVal][maxDist_index].dirtyBit = False
        elif(InstructionMode.upper() == 'W'):
            self.cache[SetVal][maxDist_index].dirtyBit = True
        self.Timer += 1

    def PLRU_Hit(self,root,tag_value,Instr):
        if(root.left == None and root.right == None):
            if((root.block.tagBit) == tag_value):
                root.block.timeStamp = self.Timer
                if Instr.upper() == 'WRITE':
                    root.block.dirtyBit = True
                self.Timer += 1
                return True

        if(root.left is not None and root.right is not None):
            if(self.PLRU_Hit(root.left,tag_value,Instr) or self.PLRU_Hit(root.right,tag_value,Instr)):
                return True
        # if():
        #     return True

    def UpdateTree(self,root,tag_val,label_address,instr,mode= 'a',MissInsert = False):
        
        while(root.block is None):
            if root.bit == 0:
                nextNode = root.left if mode == "a" else root.right
            else:
                nextNode = root.right if mode == "a" else root.left
            root.bit = 0 if root.bit else 1
            root = nextNode

        if (self.L2_Flag == False):
            if root.block.dirtyBit == True:
                self.WriteBacksCount += 1

        if (self.L2_Flag == True):
            if root.block.dirtyBit == True:
                self.WriteBacksCount += 1
        
        root.block.tagBit = tag_val
        root.block.timeStamp = self.Timer
        root.block.TagAddress = label_address
        if ((instr.upper() == 'WRITE' or instr.upper() == 'W') and MissInsert): 
            root.block.dirtyBit = True
        elif((instr.upper() == 'READ' or instr.upper() == 'R') and MissInsert): #  Missreplace flag will be true only for read instruction because there we do not change the value of dirtybit 
            root.block.dirtyBit = False
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
        #print(binary_address)
        if(int(index_bits) == 0):
            index_val = 0
        else:
            index_val = int(binary_address[int(tag_bits):32-int(offset_bits)],2)
        #print(index_val)
        tag = hex(int(binary_address[:int(tag_bits)],2))[2:]
        #tag= "{:0{}x}".format(int(binary_address[:int(tag_bits)],2),int(int(tag_bits)/4))
        #print(tag)
        #binary_address = Binary(address)
        return tag,index_val

    def CalculateCacheStats(self):
        self.Missrate = (self.ReadMissCount+self.WriteMissCount)/(self.ReadCount + self.WriteCount)
        if(self.L2_Flag):
            self.memTraffic = self.ReadMissCount + self.WriteMissCount + self.WriteBacksCount
        else:
            self.memTraffic = self.ReadMissCount + self.WriteMissCount + self.WriteBacksCount
          
    def PrintCache(self):
        if(self.replace_policy == 1):
            for i in range(self.l1_set):
                print('Set  ' , str(i),":",end= ' ')
                self.PrintLRUCache(self.cache[i])
                print('\n')
        else:
            for i in range(0,self.l1_set):
                
                print('Set  ' , str(i),":",end= ' ')
                for j in range(0,self.l1_assoc):
                    #print("\t"+str(self.cache[i][j].tagBit)+"\t"+str(self.cache[i][j].timeStamp)+"\t"+str(self.cache[i][j].dirtyBit) +"\t"+str(self.cache[i][j].IsValidBit))
                    print(str(self.cache[i][j].tagBit)," ",'D' if self.cache[i][j].dirtyBit else ' ', end=' ')
                print('\n')
        print('==========================================================')

    
    def PrintLRUCache(self,root):

        if (root.left == None and root.right == None):
            #print("\t"+str(root.block.tagBit)+"\t"+str(root.block.dirtyBit))
            print(str(root.block.tagBit),"  " ,'D'if (root.block.dirtyBit) else ' ', end=' ')

        if(root.left is not None and root.right is not None):
            self.PrintLRUCache(root.left) or self.PrintLRUCache(root.right)
               
    
    def Create_Tag_OPT(self,traceFile):

        for i in range(len(traceFile)):
            label_instruc,label_address = self.trace_file[i].split()
            tag_val,index_val = self.Calculate_Tag_Index_Offset(label_address)
            self.opt_index.append(index_val)
            self.opt_tagbits.append(tag_val)


    def SetInvalidBit_l1(self,label_instruc,label_address):
        #In this function i will set the Invalid bit for the l1 cache block.
        tag_val,index_val = self.Calculate_Tag_Index_Offset(label_address)
        # tag_val = self.OldTag_Inclusion
        # index_val = self.OldTag_Index

        for i in range(len(self.cache[index_val])):
            if (self.cache[index_val][i].tagBit == tag_val):
                self.cache[index_val][i].IsValidBit = False
                #self.cache[index_val][i].dirtyBit = True 
                break


    

    