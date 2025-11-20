import time
import hashlib
import psutil
import numpy as np
from pynput import mouse, keyboard
from collections import deque
import threading

class BaseCollector:
    def start(self):
        pass
    def stop(self):
        pass
    def collect(self, target_count):
        return np.array([])

class MouseEntropyCollector(BaseCollector):
    def collect(self, target_count):
        """
        Blocca finché non ha raccolto 'target_count' campioni dal mouse.
        """
        x_coo = []
        y_coo = []
        controller = mouse.Controller()
        
        # Loop finché non raggiungiamo il numero richiesto
        while len(x_coo) < target_count:
            x, y = controller.position
            x_coo.append(x)
            y_coo.append(y)

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
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key):
        self._buffer.append(time.perf_counter_ns())

    def collect(self, target_count):
        """
        Blocca finché l'utente non ha premuto 'target_count' tasti.
        """
        collected_timestamps = []
        
        while len(collected_timestamps) < target_count:
            if self._buffer:
                collected_timestamps.append(self._buffer.popleft())
            else:
                # Aspetta passivamente che arrivino nuovi eventi
                time.sleep(0.01)
        
        bit_k = np.zeros(len(collected_timestamps))
        for i, ts in enumerate(collected_timestamps):
            bit_k[i] = ts % 2
            
        return bit_k

class SystemEntropyCollector(BaseCollector):
    def collect(self, target_count):
        """
        Raccoglie esattamente 'target_count' bit di jitter CPU.
        """
        sys_bits = []
        perf_counter = time.perf_counter_ns
        last_time = perf_counter()
        
        # Loop basato sul conteggio
        while len(sys_bits) < target_count:
            current_time = perf_counter()
            delta = current_time - last_time
            last_time = current_time
            
            # Estrai 2 bit di entropia per campione
            sys_bits.append(delta & 1)
            if len(sys_bits) < target_count: # Controllo per non sforare
                sys_bits.append((delta >> 1) & 1)
        
        return np.array(sys_bits)
    
