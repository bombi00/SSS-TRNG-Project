import time
import uuid
import numpy as np
from pynput import mouse, keyboard
from collections import deque

class BaseCollector:
    def start(self): pass
    def stop(self): pass
    def collect(self, target_count): return np.array([])

class MouseEntropyCollector(BaseCollector):
    def collect(self, target_count):
        x_coo = []
        y_coo = []
        controller = mouse.Controller()
        # Raccoglie coordinate mouse
        while len(x_coo) < target_count:
            x, y = controller.position
            x_coo.append(x)
            y_coo.append(y)
        # Converte in bit
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
        Raccoglie fino a 'target_count' tasti dal buffer,
        MA NON BLOCCA se il buffer è vuoto.
        """
        collected_timestamps = []
        
        # Preleva dal buffer finché ce n'è o finché raggiungi il target
        while len(collected_timestamps) < target_count:
            if self._buffer:
                collected_timestamps.append(self._buffer.popleft())
            else:
                # Se il buffer è vuoto, non aspettare (sleep).
                # Interrompi e restituisci quello che hai trovato finora.
                break
        
        # Se non sono stati premuti tasti, restituisce un array vuoto.
        # Il codice in trng.py gestisce già gli array vuoti ignorandoli.
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
            print("L")
        return np.array(sys_bits)