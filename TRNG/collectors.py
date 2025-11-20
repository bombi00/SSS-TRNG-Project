import time
import hashlib
import psutil
import numpy as np
from pynput import mouse, keyboard
from collections import deque

class BaseCollector:
    def start(self):
        pass
    def stop(self):
        pass
    def collect(self, duration):
        return np.array([])

class MouseEntropyCollector(BaseCollector):
    def collect(self, duration):
        x_coo = []
        y_coo = []
        controller = mouse.Controller()
        t_end = time.time() + duration
        
        while time.time() < t_end:
            x, y = controller.position
            x_coo.append(x)
            y_coo.append(y)
            time.sleep(0.005)

        bit_m = np.zeros(len(x_coo))
        for i in range(len(x_coo)):
            val = int(x_coo[i] + y_coo[i])
            bit_m[i] = val % 2
        
        return bit_m

class KeyboardEntropyCollector(BaseCollector):
    def __init__(self):
        self._buffer = deque()
        self._listener = None

    def start(self):
        if not self._listener:
            self._listener = keyboard.Listener(on_press=self.on_press)
            self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def on_press(self):
        self._buffer.append(time.perf_counter_ns())

    def collect(self, duration):
        self._buffer.clear() 
        time.sleep(duration)
        timestamps = list(self._buffer)

        bit_k = np.zeros(len(timestamps))
        for i, ts in enumerate(timestamps):
            bit_k[i] = ts % 2
            
        return bit_k

class SystemEntropyCollector(BaseCollector):
    def collect(self, duration):
        sys_bits = []
        t_end = time.time() + duration
        
        while time.time() < t_end:
            c_stats = psutil.cpu_stats()
            n_stats = psutil.net_io_counters()
            jitter = time.perf_counter_ns()

            raw_data = f"{c_stats.ctx_switches}{c_stats.interrupts}{n_stats.bytes_recv}{jitter}"
            
            hashed = hashlib.sha256(raw_data.encode()).digest()
            sys_bits.append(hashed[-1] % 2)
            time.sleep(0.005)

        return np.array(sys_bits)