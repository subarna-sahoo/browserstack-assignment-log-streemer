import queue
from typing import Optional, List
import threading
import time

class Subscriber:
    """This is Going to be the Queue where we will also keep FIFO to handle backpressure"""
    def __init__(self, max_size: int = 100):
        self.q = queue.Queue(maxsize=max_size)
        self.active = True


    def put(self, item: str) -> None:
        if not self.active:
            return None
        try:
            self.q.put_nowait(item=item)
        except queue.Full:
            try: 
                _ = self.q.get_nowait()
                self.q.put_nowait(item)
            except Exception as e:
                print("EXC: ", e)
                pass

    def get(self, timeout: float = 1.0) -> Optional[str]:
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            print("WARN: queue is Empty")
            pass

    def close(self) -> None:
        self.active = False


class EventBus:
    """Our event bus has to be thrade safe pub-sub"""
    def __init__(self):
        self._subs: List[Subscriber] = []
        self._lock = threading.Lock()
        self._last_hb = 0.0

    def subscribe(self) -> Subscriber:
        _sub = Subscriber()
        with self._lock:
            self._subs.append(_sub)
        return _sub

    def unsubscribe(self, sub: Subscriber) -> None:
        sub.close()
        with self._lock:
            if sub in self._subs:
                self._subs.remove(sub)

    def publish(self, item: str) -> None:
        with self._lock:
            subs = list(self._subs)
        for s in subs:
            s.put(item)

    def heartbeat(self, every_seconds: float = 15.0):
        now = time.time()
        if now - self._last_hb >= every_seconds:
            self.publish("")
            self._last_hb = now