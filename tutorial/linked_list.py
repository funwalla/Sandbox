

class Node:
    
    def __init__(self, value, next=None, previous=None):
        self.value = value
        self.next = next
        self.previous = previous
        
    def __repr__(self):
        return str(self.value)

class LinkedList:
    
    def __init__(self, value):
        self.first = Node(value)

    def __repr__(self):
        current = self.first
        return_string = current.__repr__()
        while current.next != None:
            current = current.next
            return_string = return_string + " > " + current.__repr__()
        return return_string

    def add_node(self, value, position=-1):
        ''' insert node at given position.
        if position = -1, insert at the end of the list
        '''
        current = self.first
        pos = 0
        if position == 0:
            new_node = Node( value, next=self.first)
            self.first = new_node
        while current.next != None:
            current = current.next
            pos += 1
            if pos == position-1:
                the_rest = current.next
                current.next = Node(value, the_rest)
                return
        current.next = Node(value, None)
           
        
if __name__ == '__main__':
    
    #node = Node(10)
    #print node

    # Create a 10 node linked list:
    for i in range(0,10):
        if i == 0:
            ll = LinkedList(i)
        else:
            ll.add_node(i)
    print "basic list: ", ll    
    
    # add a new link in the middle
    ll.add_node('(new 2)', 2)
    print '\nnew 2:', ll
    
    # add a new link at the beginning
    ll.add_node(-1,0)
    print  '\nprepend value', ll
    
