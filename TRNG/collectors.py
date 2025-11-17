import threading
import time
import psutil
from pynput import keyboard 
from pynput.mouse import Controller as MouseController

def _mouse_worker(pool, delay_seconds=0.1):
    mouse_controller = MouseController()
    while True:
        try:
            x, y = mouse_controller.position
            valore = x + y
            bit = 0 if valore % 2 != 0 else 1
            pool.add_entropy(bit)
        except Exception as e:
            pass
        time.sleep(delay_seconds)

def start_mouse_listener(pool, delay_seconds=0.1):
    thread = threading.Thread(target=_mouse_worker, args=(pool, delay_seconds), daemon=True)
    thread.start()

def _keyboard_worker(pool):  
    press_times = {}
    def on_press(key):
        if key not in press_times:
            press_times[key] = time.perf_counter_ns()
    def on_release(key):
        if key in press_times:
            start_time = press_times.pop(key)
            durata_ns = time.perf_counter_ns() - start_time
            bit = 1 if durata_ns % 2 == 0 else 0
            pool.add_entropy(bit)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def start_keyboard_listener(pool):
    thread = threading.Thread(target=_keyboard_worker, args=(pool,), daemon=True)
    thread.start()

def _system_worker(pool, delay_seconds=0.1):
    while True:
        try:
            mem_used = psutil.virtual_memory().used
            bit = 1 if mem_used % 2 == 0 else 0
            pool.add_entropy(bit)
        except Exception as e:
            pass
        time.sleep(delay_seconds)

def start_system_listener(pool, delay_seconds=0.1):
    thread = threading.Thread(target=_system_worker, args=(pool, delay_seconds), daemon=True)
    thread.start()