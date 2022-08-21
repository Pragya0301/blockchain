import math
import numpy as np
from queue import PriorityQueue
import random
from treelib import Node, Tree

BLK_SIZE = 5


def generate_b_id(p_id, b_id):
    digits = len(str(p_id))
    p_num = p_id * (10**digits)

    return p_num + b_id


def generate_t_id(p_id, t_id):
    digits = len(str(p_id))
    p_num = p_id * (10**digits)

    return p_num + t_id


def generate_POW_time(Tk):
    return math.floor(np.random.exponential(Tk))


def generate_txn_time(Tk, last_txn_time):
    txn_time = last_txn_time + math.floor(np.random.exponential(Tk))
    return txn_time

def generate_txn_times(Tk, num_txns):
    txn_times = []
    txn_time = 0
    for i in range(num_txns):
        txn_time += math.floor(np.random.exponential(Tk))
        txn_times.append(txn_time)
    return txn_times


def random_delays(minm, maxm, n):
    return minm + np.random.randint((maxm - minm), size=(n, n))


class P2P(object):
    def __init__(self, num_peers, z, Tx):
        self.transaction_map = {}
        self.block_map = {}
        self.accounts = {}
        self.lengths = {}
        self.num_peers = num_peers
        self.peers = []
        self.genesis_block = None
        minm = 1
        maxm = 5
        num_fast = math.floor(num_peers*z/100)
        count_fast = 0
        self.T = Tx
        self.delays = random_delays(minm, maxm, self.num_peers)
        for i in range(1, num_peers+1):
            if count_fast<num_fast:
                self.peers.append(self.Peer(i,'fast', self))
            else:
                self.peers.append(self.Peer(i,'slow', self))
            count_fast += 1
        self.visual_trees = []
        for i in range(num_peers):
            self.visual_trees.append(Tree())
    
    def genesis(self):
        for i in range(self.num_peers):
            self.visual_trees[i].create_node("(b_id: 0, time: 0)", 0)
        self.genesis_block = self.Block([], 0, -1)
        self.block_map[0] = self.genesis_block
        for peer in self.peers:
            event = self.Event("cblk", -1)
            peer.add_event(1, event)

    def run(self, time):
        self.genesis()
        for i in range(1, time+1):
            print("running %d"%(i))
            # for peer in self.peers:
            #     peer.generate_peer_transactions()
            for peer in self.peers:
                peer.handle_events(i)

    class Transaction(object):
        def __init__(self, t_id, payer, receiver, amt):
            self.payer = payer
            self.receiver = receiver
            self.amt = amt
            self.t_id = t_id

    class Block(object):
        def __init__(self, txns, b_id, prev_b_id):
            self.prev_b_id = prev_b_id
            self.txns = txns
            self.b_id = b_id   

    class BlockTree:
        def __init__(self, b_id, length, peer):
            self.children = []
            self.b_id = b_id
            self.length = length
            self.accounts = {}
            self.peer = peer


    class Event(object):
        def __init__(self, typ, data):
            self.type = typ
            self.data = data

        def __gt__(self, other):
            return False

    class Peer(object):
        def __init__(self, p_id, status, p2p):
            self.p_id = p_id
            self.pending_txs = []
            self.events = PriorityQueue()
            #self.events = []
            self.next_t = 0
            self.next_b = 0
            self.p2p = p2p
            self.status = status
            self.block_tree_root = self.p2p.BlockTree(0, 1, self)
            for peer_num in range(self.p2p.num_peers):
                self.block_tree_root.accounts[peer_num] = 1000
            self.txn_time = 0
            self.txn_num = 0
            self.coins = 1000
            self.longest = [0]
            self.block_node_map = {}
            self.block_node_map[0] = self.block_tree_root

            self.txn_times = generate_txn_times(10, 2)
            for txn_num in range(1, len(self.txn_times)+1):
                t_id = generate_t_id(self.p_id, txn_num)
                self.events.put(
                    (self.txn_times[txn_num-1], self.p2p.Event("gtxn", t_id)))

        def tree_insert(self, b_id, time):
            prev_b_id = self.p2p.block_map[b_id].prev_b_id
            node_val = "(b_id: %d, time: %d)" % (b_id, time)
            self.p2p.visual_trees[self.p_id-1].create_node(node_val, b_id, parent=prev_b_id)
            is_longest = False
            parent_block_node = self.block_node_map[prev_b_id]
            block_tree_node = self.p2p.BlockTree(b_id, parent_block_node.length+1, self)
            for peer_num in range(self.p2p.num_peers):
                block_tree_node.accounts[peer_num] = 1000

            self.block_node_map[b_id] = block_tree_node
            parent_block_node.children.append(block_tree_node)
            longest_length = self.block_node_map[self.longest[0]].length
            if longest_length < block_tree_node.length:
                self.longest = [b_id]
                is_longest = True
            if longest_length == block_tree_node.length:
                self.longest.append(b_id)
            return block_tree_node, is_longest

        def generate_peer_transactions(self):
            self.txn_time = generate_txn_time(self.p2p.T, self.txn_time)
            t_id = generate_t_id(self.p_id, self.txn_num)
            self.txn_num += 1
            self.events.put((self.txn_time, self.p2p.Event("gtxn",t_id)))

        def add_event(self, time, event):
            self.events.put((time, event))

        def generate_txn(self, t_id, time):
            peer_num = 1 + np.random.randint(self.p2p.num_peers)
            if(peer_num == self.p_id):
                if(self.p_id == 1):
                    peer_num += 1
                else:
                    peer_num -= 1
            amt = np.random.uniform(1, 100, 1)
            txn = self.p2p.Transaction(t_id, self.p_id, peer_num, amt)
            self.p2p.transaction_map[txn.t_id] = txn
            # print(str(t_id)+": "+str(self.p_id)+" pays "+str(peer_num)+" "+str(amt[0])+" coins")
            for peer in self.p2p.peers:
              if(peer.p_id != self.p_id):
                  event =  self.p2p.Event("rtxn", txn.t_id)
                  peer.add_event(time+self.p2p.delays[self.p_id-1][peer.p_id-1], event)

        def receive_txn(self, t_id, time):
            # if self.p2p.peers[self.p2p.transaction_map[t_id].payer].coins >= self.p2p.transaction_map[t_id].amt:
            self.pending_txs.append(t_id)
            # print("pid %d received transaction with TxnID: %d at time: %d" % (
            #     self.p_id, t_id, time))
            # else:
            #     pass
            #     print("INVALID: pid %d received transaction with TxnID: %d at time: %d" % (
            #         self.p_id, t_id, time))

        def receive_block(self, b_id, time):
            print("pid %d received block with BlkID: %d at time: %d" %
                  (self.p_id, b_id, time))
            if self.verify_block(b_id, time):

                for txn in self.p2p.block_map[b_id].txns:
                    self.rem_txn(txn)
                
                block = self.p2p.block_map[b_id]
                block_tree_node, is_longest = self.tree_insert(b_id, time)
                block_tree_parent = self.block_node_map[block.prev_b_id]


                for txn in self.p2p.block_map[b_id].txns:
                    payer = self.p2p.transaction_map[txn].payer
                    receiver = self.p2p.transaction_map[txn].receiver
                    amt = self.p2p.transaction_map[txn].amt
                    # self.p2p.peers[self.p2p.transaction_map[txn].payer].coins -= self.p2p.transaction_map[txn].amt
                    # self.p2p.peers[self.p2p.transaction_map[txn].receiver].coins += self.p2p.transaction_map[txn].amt
                    block_tree_node.accounts[payer-1] = block_tree_parent.accounts[payer-1] - amt
                    block_tree_node.accounts[receiver-1] = block_tree_parent.accounts[receiver-1] + amt
                if is_longest:
                    self.create_block(time)

            else:
                print("INVALID!!")

        def verify_block(self, b_id, time):
            block = self.p2p.block_map[b_id]
            try:
                parent_block_node = self.block_node_map[block.prev_b_id]
            except:
                return False

            pay_sum = []
            for i in range(self.p2p.num_peers):
                pay_sum.append(0)

            for t_id in block.txns:
                amt = self.p2p.transaction_map[t_id].amt
                payer_id = self.p2p.transaction_map[t_id].payer
                pay_sum[payer_id-1] += amt
                if parent_block_node.accounts[payer_id-1] < pay_sum[payer_id-1]:
                    # print("INVALID: pid %d trying to pay more than %d in BlkID: %d" % (
                    #     self.p_id, parent_block_node.accounts[payer_id-1], b_id))
                    return False

            print("BlkID: %d verified at time: %d" % (
                b_id, time))

            return True

        def rem_txn(self, t_id):
            try:
                self.pending_txs.remove(t_id)
            except:
                pass

        def create_block(self, time):
            txns = []
            if len(self.pending_txs) < BLK_SIZE:
                txns = self.pending_txs
            else:
                txns = random.sample(self.pending_txs, BLK_SIZE)
                # remove from pending transactions when broadcast

            self.next_b += 1
            b_id = generate_b_id(self.p_id, self.next_b)
            current_block = self.p2p.Block(
                txns, b_id, self.longest[0])
            self.p2p.block_map[b_id] = current_block
            Tk = 20
            tk = 2 + generate_POW_time(Tk)
            # print("pid %d created BlkID: %d at time %d" % (
            #     self.p_id, b_id, time))
            event = self.p2p.Event("bblk", b_id)
            self.events.put((time + tk, event))

        def broadcast_block(self, b_id, time):
            current_block = self.p2p.block_map[b_id]
            if self.longest[0] == current_block.prev_b_id:
                print("pid %d broadcasted BlkID: %d at time %d" % (
                    self.p_id, b_id, time))
                # for txn in current_block.txns:
                #     try:
                #         self.pending_txs.remove(txn)
                #     except:
                #         pass
                for peer in self.p2p.peers:
                    if(peer.p_id != self.p_id):
                        event = self.p2p.Event("rblk", b_id)
                        peer.add_event(
                            time+self.p2p.delays[self.p_id-1][peer.p_id-1], event)
                self.receive_block(b_id, time)


        def handle_events(self, time):
            if self.events.empty():
                return
            event_time, event = self.events.get()
            while event_time == time:
                if(event.type == "gtxn"):
                    self.generate_txn(event.data, time)
                if(event.type == "rtxn"):
                    self.receive_txn(event.data, time)
                if(event.type == "rblk"):
                    self.receive_block(event.data, time)
                if(event.type == "cblk"):
                    self.create_block(time)
                if(event.type == "bblk"):
                    self.broadcast_block(event.data, time)
                if self.events.empty():
                    return
                event_time, event = self.events.get()
            self.events.put((event_time, event))


# T = int(input("give T"))
# p2p = P2P(int(input("number of peers")), int(input("percentage of fast peers")), T)
p2p = P2P(5, 2, 5)
p2p.run(40)
for i in range(p2p.num_peers):
    print("Blockchain tree of peer: %d"%(i+1))
    p2p.visual_trees[i].show()
