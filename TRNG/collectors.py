
import threading
import time
import psutil
from pynput import keyboard 
from pynput.mouse import Controller as MouseController

def _mouse_worker(pool, stop_event, delay_seconds=0.1):
    mouse_controller = MouseController()

    while not stop_event.is_set():
        try:
            x, y = mouse_controller.position
            valore = x + y
            bit = 0 if valore % 2 != 0 else 1
            pool.add_entropy(bit)

        except Exception as e:
            print(f"[Errore Collettore Mouse]: {e}")
        stop_event.wait(timeout=delay_seconds)
        

def start_mouse_listener(pool, stop_event, delay_seconds=0.1):
    thread = threading.Thread(target=_mouse_worker, args=(pool, stop_event, delay_seconds), daemon=True)
    thread.start()
    return thread

def _keyboard_worker(pool, stop_event):  
    press_times = {}

    def on_press(key):
        if key not in press_times:
            press_times[key] = time.perf_counter_ns()

    def on_release(key):
        if key in press_times:
            start_time = press_times.pop(key)
            end_time = time.perf_counter_ns()
            durata_ns = end_time - start_time
            
            bit = 1 if durata_ns % 2 == 0 else 0
            pool.add_entropy(bit) #
            
            if stop_event.is_set():
                return False

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    stop_event.wait()
    listener.stop()

def start_keyboard_listener(pool, stop_event):
    thread = threading.Thread(target=_keyboard_worker, args=(pool, stop_event), daemon=True)
    thread.start()
    return thread


def _system_worker(pool, stop_event, delay_seconds=0.1):
    while not stop_event.is_set():
        try:
            mem_used = psutil.virtual_memory().used
            bit = 1 if mem_used % 2 == 0 else 0
            pool.add_entropy(bit) #
        except Exception as e:
            print(f"[Errore Collettore Memoria]: {e}")
            
        stop_event.wait(timeout=delay_seconds)
            

def start_system_listener(pool, stop_event, delay_seconds=0.1):
    thread = threading.Thread(target=_system_worker, args=(pool, stop_event, delay_seconds), daemon=True)
    thread.start()
    return thread