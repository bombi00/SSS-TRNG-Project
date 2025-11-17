import math
from entropyPool import EntropyPool
import collectors
import threading

class EntropyTRNG:

    def __init__(self, system_poll_interval=0.1):
        self.pool = EntropyPool()
        self.buffer = bytearray()
        self.system_poll_interval = system_poll_interval
        
        self._start_collectors_daemon()

    def _start_collectors_daemon(self):
        collectors.start_mouse_listener(self.pool, self.system_poll_interval)
        collectors.start_keyboard_listener(self.pool)
        collectors.start_system_listener(self.pool, self.system_poll_interval)

    def _fill_buffer(self):
        self.buffer.extend(self.pool.get_hash())

    def get_random_bytes(self, n_bytes):
        result = bytearray()
        while len(result) < n_bytes:
            if not self.buffer:
                self._fill_buffer()

            needed = n_bytes - len(result)
            
            chunk_size = min(needed, len(self.buffer))
            chunk = self.buffer[:chunk_size]
            
            self.buffer = self.buffer[chunk_size:]
            
            result.extend(chunk)
            
        return bytes(result)

    def get_random_int(self, min_val, max_val):
        if min_val > max_val:
            raise ValueError("min_val non può essere maggiore di max_val")
            
        range_val = max_val - min_val + 1
        num_bits = range_val.bit_length()
        num_bytes = math.ceil(num_bits / 8)
        
        max_acceptable = (2**(num_bytes * 8) // range_val) * range_val
        
        while True:
            rand_bytes = self.get_random_bytes(num_bytes)
            rand_int = int.from_bytes(rand_bytes, 'little')
            
            if rand_int < max_acceptable:
                return (rand_int % range_val) + min_val

    def get_random_float(self):
        rand_bytes = self.get_random_bytes(8)
        rand_int = int.from_bytes(rand_bytes, 'little')
        
        return rand_int / (2**64)