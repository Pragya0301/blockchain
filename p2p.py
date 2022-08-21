import numpy as np
import random
import time

class Block:
    def __init__(self):
        self.txn_list = []
        self.total_txn = 0
        self.who_paid = 0
        self.to_whom = 0
        self.amount = 0
        self.txn_id = 0
    
    def txn(self, txn_string):
        self.txn_list.append(txn_string)
        tokens = txn_string.split()
        self.txn_id = tokens[0][:-1]
        self.who_paid = tokens[1]
        self.to_whom = tokens[3]
        self.amount = tokens[4]
        
        
        

class Peer:
    def __init__(self, ID):
        self.coin = 1000
        self.ID = ID
        
    def show(self):
        return 1
    
    def give_coins(self):
        return self.coin
    
        
    # todo status(slow or fast)
    
    

if __name__=="__main__":
    n = int(input())
    total_txn = 101
    T = int(input())
    
    IDs = random.sample(range(100000, 1000000), n)
    
    peers=[]
    
    for i in range(n):
        peers.append(Peer(IDs[i]))
    
    i=0
    while(i<total_txn):
        rnd_x = random.sample(IDs, 1)
        rnd_y = random.sample(IDs, 1)
        C = np.random.uniform(1, peers[IDs.index(rnd_x)].give_coins()+1, 1)
        
        if rnd_x == rnd_y:
            i-=1
            continue
        
        interval = np.random.exponential(T)
        
        txn_id = hash(str(i)+str(rnd_x)+str(rnd_y)+str(C))
        txn_string = str(txn_id) + ": " + str(rnd_x) + " pays " + str(rnd_y) + " " + str(C) + " coins"
        
        
        time.sleep(interval)