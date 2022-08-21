import math
import numpy as np
from queue import PriorityQueue

def generate_b_id(p_id, b_id):
	digits = len(str(p_id))
	p_num = p_id * (10**digits)

	return p_num + b_id


def generate_t_id(p_id, t_id):
	digits = len(str(p_id))
	p_num = p_id * (10**digits)

	return p_num  + t_id

def generate_POW_time(Tk):
	return math.floor(np.random.exponential(Tk))

def generate_txn_times(Tk, num_txns):
	txn_times = []
	txn_time = 0
	for i in range(num_txns):
		txn_time += math.floor(np.random.exponential(Tk))
		txn_times.append(txn_time)
	return txn_times

def random_delays(minm, maxm, n):
	return minm + np.random.randint((maxm - minm), size=(n,n))
		

class P2P(object):
	def __init__(self, num_peers):
		self.transaction_map = {}
		self.block_map = {}
		self.account = {}
		self.num_peers = num_peers
		self.peers = []
		minm = 1
		maxm = 5
		self.delays = random_delays(minm, maxm, self.num_peers)
		for i in range(1, num_peers+1):
			self.peers.append(self.Peer(i,self))

	def genesis(self):
		pass

	def run(self, time):
		for i in range(1, time+1):
			print("running %d"%(i))
			for peer in self.peers:
				peer.handle_events(i)

	class Transaction(object):
		def __init__(self, t_id, payer, receiver, amt):
			self.payer = 0
			self.receiver = 0
			self.amt = 0
			self.t_id = t_id


	class Block(object): 
	    def __init__(self, b_id):
	    	self.txns = []
	    	self.b_id = b_id

	class Event(object):
		def __init__(self, typ, data):
			self.type = typ
			self.data = data

		def __gt__(self, other):
			return False

	class Peer(object):
	    def __init__(self, p_id, p2p):
	    	self.p_id = p_id
	    	self.pending_txs = {}
	    	self.events = PriorityQueue()
	    	self.next_t = 0
	    	self.next_b = 0
	    	self.p2p = p2p
	    	self.current_block = self.p2p.Block(0)
	    	self.block_chain = []
	    	self.txn_times = generate_txn_times(10, 5)
	    	for txn_num in range(1, len(self.txn_times)+1):
	    		t_id = generate_t_id(self.p_id, txn_num)
	    		self.events.put((self.txn_times[txn_num-1], self.p2p.Event("gtxn",t_id)))

	    def add_event(self, time, event):
	    	self.events.put((time, event))

	    def generate_txn(self, t_id, time):
	    	peer_num = 1 + np.random.randint(self.p2p.num_peers+1)
	    	if(peer_num == self.p_id):
	    		if(self.p_id == 1):
	    			peer_num += 1
	    		else:
	    			peer_num -= 1
	    	amt = 1
	    	txn = self.p2p.Transaction(t_id, self.p_id, peer_num, amt)
	    	self.p2p.transaction_map[txn.t_id] = txn
	    	print("pid %d generated a transaction with TxnID: %d at time: %d"%(self.p_id, t_id, time))
	    	for peer in self.p2p.peers:
	    		if(peer.p_id != self.p_id):
		    		event =  self.p2p.Event("rtxn", txn.t_id)
		    		peer.add_event(time+self.p2p.delays[self.p_id-1][peer.p_id-1], event)

	    def receive_txn(self, t_id, time):
	    	print("pid %d received transaction with TxnID: %d at time: %d"%(self.p_id, t_id, time))

	    def receive_block(self, b_id):
	    	pass

	    def verify_block(self, b_id):
	    	pass

	    def rem_txn(self, t_id):
	    	pass

	    def create_block(self):
	    	pass

	    def broadcast_block(self):
	    	pass

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
	    			self.receive_block(event.data)
	    		if(event.type == "bblk"):
	    			self.broadcast_block()
			if self.events.empty():
				return
	    		event_time, event = self.events.get()
	    	self.events.put((event_time, event))



p2p = P2P(5)
p2p.run(100)
