import time
import threading
import queue


class FloodControl:
	X_LINES = 1
	Y_SECONDS = 1
	equeue = queue.PriorityQueue()
	
	def __init__(self):
		flood_thread = threading.Thread(target=self.process_msg)
		flood_thread.start()

	@staticmethod
	def get_event(priority):
		e = threading.Event()
		e.clear()
		FloodControl.equeue.put((priority, e))
		return e

	def process_msg(self):
		while True:
			if not FloodControl.equeue.empty():
				priority, e = FloodControl.equeue.get()
				e.set()
			time.sleep(FloodControl.Y_SECONDS)
