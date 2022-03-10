import CachBlock


class Node:

    def __init__(self, lNode = None,rNode=None,pNode=None):

        #self.NodeId = NodeId
        self._left = lNode
        self._right = rNode
        self.pNode = pNode
        self._block = None
        self.bit = -1
    @property
    def block(self):
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

    @left.setter
    def left(self, node):
        # Union node.hashMap & self.hashMap
        self._left = node

    @property
    def right(self):
        if self._right is None:
            pass
        return self._right

    @right.setter
    def right(self, node):
        # Union node.hashMap & self.hashMap
        self._right = node
      