import heapq

class sqsheapq:
	def __init__(self, seqnum):
		self.heaplist = []
		self.seqnum = seqnum
		self.counter = 0
	def remove(self):
		if self.seqnum == self.heaplist[0][0] and self.counter > 0
			item = heapq.heappop(self.heaplist)
			self.counter -= 0
			#duplicates
			while self.counter > 0 and self.heaplist[0] == item:
				heapq.heappop(self.heaplist)
				self.counter -= 0
			self.seqnum = 1
			return item
		else:
			return ""
	def add(self, op, seq_num):
		heapq.heappush(self.heaplist, (seq_num, op))
		self.counter += 1
	def getTop():
		return self.heaplist[0]