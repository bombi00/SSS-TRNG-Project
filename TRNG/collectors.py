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
    def collect(self, duration):
        return np.array([])

class MouseEntropyCollector(BaseCollector):
    def collect(self, duration):
        """Campiona la posizione del mouse per la durata richiesta."""
        x_coo = []
        y_coo = []
        controller = mouse.Controller()
        t_end = time.time() + duration
        
        # Campionamento ad alta frequenza (~100Hz)
        while time.time() < t_end:
            x, y = controller.position
            x_coo.append(x)
            y_coo.append(y)
            time.sleep(0.005) # Sleep breve per non saturare la CPU

        if not x_coo: return np.array([])

        # Estrazione bit meno significativo dalla somma coordinate
        bit_m = np.zeros(len(x_coo))
        for i in range(len(x_coo)):
            val = int(x_coo[i] + y_coo[i])
            bit_m[i] = val % 2
        
        return bit_m

class KeyboardEntropyCollector(BaseCollector):
    def __init__(self):
        self._buffer = deque() # Coda thread-safe per i timestamp
        self._listener = None

    def start(self):
        if not self._listener:
            # Avvia il listener una volta sola in background
            self._listener = keyboard.Listener(on_press=self._on_press)
            self._listener.start()
            print("[Keyboard] Listener avviato in background.")

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key):
        # Salva il timestamp in nanosecondi
        self._buffer.append(time.perf_counter_ns())

    def collect(self, duration):
        # Svuota il buffer corrente e attendi per la durata
        # Nota: Non fermiamo il listener! Raccogliamo solo ciò che arriva.
        self._buffer.clear() 
        time.sleep(duration)
        
        # Preleva i dati accumulati nel buffer
        timestamps = list(self._buffer)
        
        if not timestamps:
            return np.array([])

        bit_k = np.zeros(len(timestamps))
        for i, ts in enumerate(timestamps):
            # Usa i nanosecondi per massima entropia
            bit_k[i] = ts % 2
            
        return bit_k

class SystemEntropyCollector(BaseCollector):
    def collect(self, duration):
        """Raccoglie jitter di sistema e contatori hardware."""
        sys_bits = []
        t_end = time.time() + duration
        
        while time.time() < t_end:
            c_stats = psutil.cpu_stats()
            n_stats = psutil.net_io_counters()
            
            # Jitter temporale in nanosecondi (sempre variabile)
            jitter = time.perf_counter_ns()
            
            # Snapshot dello stato del sistema
            raw_data = f"{c_stats.ctx_switches}{c_stats.interrupts}{n_stats.bytes_recv}{jitter}"
            
            # Hashing immediato per sbiancamento (Whitening)
            hashed = hashlib.sha256(raw_data.encode()).digest()
            sys_bits.append(hashed[-1] % 2)
            
            time.sleep(0.005) # 200Hz sampling
        
        return np.array(sys_bits)