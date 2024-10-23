import hashlib
m = 9
MAX = 2**m -1


def decrease(current,size):
    if size <= current:
        return current-size
    else:
        return MAX-(size-current)


def between(current,init,end):
    if init < end:
        return init < current < end
    return init < current or current < end


def check_if_first(current,init,end):
    if current == init:
        return True
    else:
        return between(current,init,end)


def check_if_last(current,init,end):
    if current == end:
        return True
    else:
        return between(current,init,end)


class Node:
    def __init__(self, node_id, university):
        self.node_id = node_id
        self.university = university
        self.finger = {}
        self.start = {}
        self.scientists = {}
        for i in range(m):
            self.start[i] = (self.node_id+(2**i)) % 2**m

    def add_scientist(self, scientist):
        # vazoume tous epistimones sto successor node tou panepistimiou sto opoio anikoun
        for university in scientist.education:
            hashed_uni = Node.hash_function(university)
            next_node = self.find_successor(hashed_uni)

            if university not in next_node.scientists:
                next_node.scientists[university] = []
            next_node.scientists[university].append(scientist)

    @staticmethod
    def hash_function(key):
        return int(hashlib.sha1(key.encode('utf-8')).hexdigest(), 16) % MAX

    def successor(self):
        return self.finger[0]

    def find_successor(self,id):
        if check_if_last(id,self.predecessor.node_id,self.node_id):
            return self
        n = self.find_predecessor(id)
        return n.successor()

    def find_predecessor(self,id):
        if id == self.node_id:
            return self.predecessor
        n = self
        while not check_if_last(id,n.node_id,n.successor().node_id):
            n = n.closest_preceding_finger(id)
        return n

    def closest_preceding_finger(self,id):
        for i in range(m-1, -1, -1):
            if between(self.finger[i].node_id,self.node_id,id):
                return self.finger[i]
        return self

    def join(self,first_node):
        if self == first_node:
            self.predecessor = self
            for i in range(m):
                self.finger[i] = self
        else:
            self.init_finger_table(first_node)
            self.update_others()

    def init_finger_table(self, n):
        self.finger[0] = n.find_successor(self.start[0])
        self.predecessor = self.successor().predecessor
        self.successor().predecessor = self
        self.predecessor.finger[0] = self

        for i in range(m-1):
            if check_if_first(self.start[i+1],self.node_id,self.finger[i].node_id):
                self.finger[i+1] = self.finger[i]
            else:
                self.finger[i+1] = n.find_successor(self.start[i+1])

    def update_others(self):
        for i in range(m):
            prev = decrease(self.node_id,2**m)
            p = self.find_predecessor(prev)
            if prev == p.successor().node_id:
                p = p.successor()
            p.update_finger_table(self,i)

    def update_finger_table(self,new_node,i):
        if self.node_id!=new_node.node_id and check_if_first(new_node.node_id, self.node_id, self.finger[i].node_id) :
            self.finger[i] = new_node
            p = self.predecessor
            p.update_finger_table(new_node,i)

    def update_others_leave(self):
        for i in range(m):
            prev = decrease(self.node_id,2**i)
            p = self.find_predecessor(prev)
            p.update_finger_table(self.successor(),i)

    def leave(self):
        self.predecessor.finger[0] = self.successor()
        self.successor().predecessor = self.predecessor
        self.update_others_leave()

    def print_ring(first_node):
        visited = set()
        current_node = first_node
        print()
        print("---Chord Ring---")
        while current_node not in visited:
            visited.add(current_node)

            print(f"Node ID: {current_node.node_id}, University: {current_node.university}")
            if current_node.successor() is not None:
                print(f"  Successor: {current_node.successor().node_id}")
            else:
                print("  Successor: None")

            if current_node.predecessor is not None:
                print(f"  Predecessor: {current_node.predecessor.node_id}")
            else:
                print("  Predecessor: None")
            print("  ----------")

            if current_node.successor() and current_node.successor() != current_node:
                current_node = current_node.successor()
            else:
                break

        if current_node == first_node:
            print("Completed!!!")
        else:
            print("Uh-oh!! There's an error...ring not completed ;(")
