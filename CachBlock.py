
class Create_Block:
    def __init__(self):
    #Intializing the tag bit, timestamp, dirtyFlag.
        self.tagBit = ""            #added to store the tag value
        self.timeStamp = -1         #added to find which bit is the earliest
        self.dirtyBit = False       #added to store the dirty bit
        self.IsValidBit = False     #initally the bit would be invalid. Once the new tag would be added the flag will be set to True.
        self.TagAddress = ""        #added to store the original address of the tag


class PLRUNode:
    def __init__(self, lNode = None,rNode=None,pNode=None):
        self._left = lNode
        self._right = rNode
        self.pNode = pNode
        self._block = None
        self.bit = -1
    
    @property
    def block(self):  #This will help in storing the cache block at the leaf node
        if self._block is None:
            pass
        return self._block

    @block.setter
    def block(self,blockval):
        if self.left or self.right:
            pass
        self._block = blockval

    @property
    def left(self):
        if self._left is None:
            pass
        return self._left

    @left.setter  #For the left node value
    def left(self, node):
        self._left = node

    @property
    def right(self):
        if self._right is None:
            pass
        return self._right

    @right.setter  #For the right node value
    def right(self, node):
        self._right = node