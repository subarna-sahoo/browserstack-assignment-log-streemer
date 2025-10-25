import io
import threading
import time
from event_bus import EventBus

class AbstractTailer(threading.Thread):
    daemon = True

    def __init__(self, path: str, bus: EventBus, poll_interval: float = 0.2, encoding="utf-8"):
        super().__init__()

        self.path = path
        self.bus = bus
        self.poll_interval = poll_interval
        self._stop = threading.Event()
    
    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        with open(self.path, "rb") as raw:
            raw.seek(0, 2)
            reader = self._wrap_reader(raw)
            reader.seek(0, 2)
            carry = ""
            while not self._stop.is_set():
                chunk = reader.read()
                if chunk:
                    data = carry + chunk
                    carry, records = self._frame(data)
                    for rec in records:
                        self.bus.publish(rec)
                else:
                    self.bus.heartbeat()
                    time.sleep(self.poll_interval)

    def _wrap_reader(self, raw) -> io.TextIOWrapper:
        raise NotImplementedError
    
    def _frame(self, buffer:str) -> tuple[str, list]:
        raise NotImplementedError
    

class NewlineFramedTailer(AbstractTailer):
    def __init__(self, path:str, bus:EventBus, poll_interval = 0.2, encoding= "utf-8"):
        super().__init__(path, bus, poll_interval, encoding)
        self.encoding = encoding

    def _wrap_reader(self, raw):
        return io.TextIOWrapper(raw, encoding=self.encoding, errors="replace", newline="")
    
    def _frame(self, buffer):
        parts = buffer.split("\n")
        carry = parts.pop()
        return carry, parts
