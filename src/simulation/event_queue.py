import heapq


class EventQueue:
    def __init__(self):
        self.events = []

    def push(self, event):
        heapq.heappush(self.events, (event.time, event))

    def pop(self):
        return heapq.heappop(self.events)[1]

    def is_empty(self):
        return len(self.events) == 0
