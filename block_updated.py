import math
import numpy as np
from queue import PriorityQueue
import random

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


def random_delays(minm, maxm, n):
    return minm + np.random.randint((maxm - minm), size=(n, n))


class P2P(object):
    def __init__(self, num_peers, z, Tx):
        self.transaction_map = {}
        self.block_map = {}
        self.account = {}
        self.num_peers = num_peers
        self.peers = []
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

    def genesis(self):
        for peer in self.peers:
            peer.block_chain.append(0)
        for peer in self.peers:
            event = self.Event("cblk", -1)
            peer.add_event(1, event)

    def run(self, time):
        for i in range(1, time+1):
            print("running %d"%(i))
            for peer in self.peers:
                peer.generate_peer_transactions()
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
            self.current_block = self.p2p.Block(None, None, None)
            self.block_chain = []
            self.txn_time = 0
            self.txn_num = 0
            self.coins = 1000

        def generate_peer_transactions(self):
            self.txn_time = generate_txn_time(self.p2p.T, self.txn_time)
            t_id = generate_t_id(self.p_id, self.txn_num)
            self.txn_num += 1
            self.events.put((self.txn_time, self.p2p.Event("gtxn",t_id)))

        def add_event(self, time, event):
            self.events.put((time, event))

        def generate_txn(self, t_id, time):
            peer_num = 1 + np.random.randint(self.p2p.num_peers+1)
            if(peer_num == self.p_id):
                if(self.p_id == 1):
                    peer_num += 1
                else:
                    peer_num -= 1
            amt = np.random.uniform(1, self.coins+1, 1)
            txn = self.p2p.Transaction(t_id, self.p_id, peer_num, amt)
            self.p2p.transaction_map[txn.t_id] = txn
            print(str(t_id)+": "+str(self.p_id)+" pays "+str(peer_num)+" "+str(amt[0])+" coins")
            #for peer in self.p2p.peers:
            #   if(peer.p_id != self.p_id):
            #       event =  self.p2p.Event("rtxn", txn.t_id)
            #       peer.add_event(time+self.p2p.delays[self.p_id-1][peer.p_id-1], event)

        def receive_txn(self, t_id, time):
            if self.p2p.peers[self.p2p.transaction_map[t_id].payer].coins >= self.p2p.transaction_map[t_id].amt:
                self.pending_txs.append(t_id)
                print("pid %d received transaction with TxnID: %d at time: %d" % (
                    self.p_id, t_id, time))
            else:
                pass
                print("INVALID: pid %d received transaction with TxnID: %d at time: %d" % (
                    self.p_id, t_id, time))

        def receive_block(self, b_id, time):
            print("pid %d received block with BlkID: %d at time: %d" %
                  (self.p_id, b_id, time))
            if self.verify_block(b_id, time):
                self.block_chain.append(b_id)
                if b_id != self.current_block.b_id:
                    for txn in self.p2p.block_map[self.block_chain[-1]].txns:
                        self.rem_txn(txn)
                self.create_block(time)
            else:
                print("INVALID!!")

        def verify_block(self, b_id, time):
            block = self.p2p.block_map[b_id]
            if (block.prev_b_id != self.block_chain[-1]):
                return False

            pay_sum = []
            for i in range(self.p2p.num_peers):
                pay_sum.append(0)

            present_amt = []
            for i in range(self.p2p.num_peers):
                present_amt.append(1000)
            for blk_id in self.block_chain:
                if blk_id == 0:
                    continue
                blk = self.p2p.block_map[blk_id]
                for t_id in blk.txns:
                    amt = self.p2p.transaction_map[t_id].amt
                    payer_id = self.p2p.transaction_map[t_id].payer
                    receiver_id = self.p2p.transaction_map[t_id].receiver
                    present_amt[payer_id-1] -= amt
                    present_amt[receiver_id-1] += amt

            for t_id in block.txns:
                amt = self.p2p.transaction_map[t_id].amt
                payer_id = self.p2p.transaction_map[t_id].payer
                pay_sum[payer_id-1] += amt
                if present_amt[payer_id-1] < pay_sum[payer_id-1]:
                    print("INVALID: pid %d trying to pay more than %d in BlkID: %d" % (
                        self.p_id, present_amt[payer_id-1], b_id))
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
            self.current_block = self.p2p.Block(
                txns, b_id, self.block_chain[-1])
            self.p2p.block_map[b_id] = self.current_block
            Tk = 20
            tk = 5 + generate_POW_time(Tk)
            print("pid %d created BlkID: %d at time %d" % (
                self.p_id, b_id, time))
            event = self.p2p.Event("bblk", b_id)
            self.events.put((time + tk, event))

        def broadcast_block(self, time):
            if self.block_chain[-1] == self.current_block.prev_b_id:
                print("pid %d broadcasted BlkID: %d at time %d" % (
                    self.p_id, self.current_block.b_id, time))
                for txn in self.current_block.txns:
                    try:
                        self.pending_txs.remove(txn)
                    except:
                        pass
                for peer in self.p2p.peers:
                    if(peer.p_id != self.p_id):
                        event = self.p2p.Event("rblk", self.current_block.b_id)
                        peer.add_event(
                            time+self.p2p.delays[self.p_id-1][peer.p_id-1], event)
                self.receive_block(self.current_block.b_id, time)
            else:
                self.current_block = self.p2p.Block(None, None, None)

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
                    self.broadcast_block(time)
                if self.events.empty():
                    return
                event_time, event = self.events.get()
            self.events.put((event_time, event))


T = int(input("give T"))
p2p = P2P(int(input("number of peers")), int(input("percentage of fast peers")), T)
p2p.run(100)