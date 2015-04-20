import heapq

class sqsheapq:
	def __init__(self, seqnum):
		self.heaplist = []
		self.seqnum = 0
		self.seqnum = seqnum
		self.counter = 0
	def remove(self):
		#heaplist[0][0] returns a the heap number
		if self.seqnum == self.heaplist[0][0] and self.counter > 0:
			item = heapq.heappop(self.heaplist)
			self.counter -= 1
			#duplicates if item is the same as heaplist[0]
			while self.counter > 0 and self.heaplist[0] == item:
				heapq.heappop(self.heaplist)
				self.counter -= 1
			self.seqnum += 1
			return item
		else:
			return ""
	def add(self, seq_num, op):
		heapq.heappush(self.heaplist, (seq_num, op))
		self.counter += 1
	def getTop(self):
		return self.heaplist[0][0]