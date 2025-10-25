from typing import List

class LastNStrategy:

    def read_last_n(self, path: str, n:int) -> List[str]:
        raise NotImplementedError
    

class BlockScanLastN(LastNStrategy):
    def __init__(self, block_size = 8192, encoding="utf-8"):
        self.block_size = block_size
        self.encoding = encoding

    def read_last_n(self, path:str, n:int):
        if n <= 0:
            return []
        lines: List[bytes] = []
        with open(path, "rb") as f:
            f.seek(0, 2) 
            pos = f.tell()
            buf = b""
            while pos > 0 and len(lines) <= n:
                size = self.block_size if pos > self.block_size else pos
                pos -= size
                f.seek(pos)
                chunk = f.read(size)
                buf = chunk + buf
                parts = buf.split(b"\n")
                buf = parts[0]
                lines = parts[1:] + lines
            if buf and len(lines) < n:
                lines = [buf] + lines
            
        return [b.decode(self.encoding, errors="replace") for b in lines[-n:]]
        