import heapq


class EventQueue:
    def __init__(self):
        self.events = []
        self.counter = 0

    def push(self, event):

        heapq.heappush(self.events, (event.time, self.counter, event))

        self.counter += 1

    def pop(self):

        return heapq.heappop(self.events)[2]

    def is_empty(self):

        return len(self.events) == 0
