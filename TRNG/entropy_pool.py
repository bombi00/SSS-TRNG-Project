import hashlib
import threading
import time
import os

class EntropyPool:
    MAX_POOL_SIZE = 8192 

    def __init__(self):
        self.pool = bytearray()
        self.lock = threading.Lock()
        self.add_entropy(os.urandom(1024))

    def add_entropy(self, *data_args):
        timestamp_ns = time.perf_counter_ns().to_bytes(8, 'little', signed=False)
        data_str = str(data_args).encode('utf-8')
        
        with self.lock:
            self.pool.extend(timestamp_ns)
            self.pool.extend(data_str)
            if len(self.pool) > self.MAX_POOL_SIZE:
                self.pool = self.pool[-self.MAX_POOL_SIZE:]

    def get_hash(self):
        with self.lock:
            if len(self.pool) == 0:
                # Caso limite: se il pool è vuoto, aggiungi comunque qualcosa
                self.add_entropy("init_warning")

            hasher = hashlib.sha256()
            hasher.update(self.pool)
            digest = hasher.digest()
            
            self.pool.extend(digest)
            
            if len(self.pool) > self.MAX_POOL_SIZE:
                self.pool = self.pool[-self.MAX_POOL_SIZE:]
                
            return digest