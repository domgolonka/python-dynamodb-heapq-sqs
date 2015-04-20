import heapq
import heap

h = heap.sqsheapq(1)

h.add(1, 'hello')
h.add(2, 'create')
h.add(3, 'retrieve')
h.add(4, 'add')

print h.remove()
print h.remove()


h.add(2, 'create')
h.add(3, 'create2')

print h.remove()



h.getTop()