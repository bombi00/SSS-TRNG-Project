import threading
import time
import psutil
from pynput import mouse, keyboard

def _mouse_worker(pool):
    def on_move(x, y):
        pool.add_entropy("mouse_move", x, y)

    def on_click(x, y, button, pressed):
        pool.add_entropy("mouse_click", x, y, str(button), pressed)

    def on_scroll(x, y, dx, dy):
        pool.add_entropy("mouse_scroll", x, y, dx, dy)

    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()

def start_mouse_listener(pool):
    thread = threading.Thread(target=_mouse_worker, args=(pool,), daemon=True)# da capire il significato
    thread.start()


def _keyboard_worker(pool):
    
    def on_press(key):
        pool.add_entropy("key_press") 
    def on_release(key):
        pool.add_entropy("key_release")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def start_keyboard_listener(pool):
    thread = threading.Thread(target=_keyboard_worker, args=(pool,), daemon=True)
    thread.start()


def _system_worker(pool, delay_seconds):
    while True:
        cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()       
        disk_io = psutil.disk_io_counters()        
        net_io = psutil.net_io_counters()   
        pool.add_entropy("system_stats", cpu_percent, mem.percent, disk_io.read_bytes, disk_io.write_bytes, net_io.bytes_sent, net_io.bytes_recv)
        time.sleep(delay_seconds)
    

def start_system_listener(pool, delay_seconds=0.1):
    thread = threading.Thread(target=_system_worker, args=(pool, delay_seconds), daemon=True)
    thread.start()