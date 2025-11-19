import time
import hashlib
from pynput import mouse, keyboard
import psutil
import matplotlib.pyplot as plt
import numpy as np

def showMousePositions(x, y):
    plt.figure(figsize=(16, 9))
    plt.scatter(x, y, s=1)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Mouse positions")
    plt.show()

def showBitSeq(seq, title="Bit sequence"):
    plt.figure(figsize=(20, 4))
    plt.plot(range(len(seq)), seq)
    plt.ylim(-0.2, 1.2)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title(title)
    plt.grid(True)
    plt.show()


def collectMouseEntropy(plot_mouse=True, plot_bit=True, seconds=15):
    x_coo = []
    y_coo = []
    controller = mouse.Controller()
    print("Move the mouse...\n")
    time.sleep(2)
    t_end = time.time() + seconds
    while time.time() < t_end:
        x, y = controller.position
        x_coo.append(x)
        y_coo.append(y)

    if plot_mouse:
        showMousePositions(x_coo, y_coo)
    
    bit_m = np.zeros(shape=(len(x_coo)))
    for i in range(len(x_coo)):
        temp = int(x_coo[i] + y_coo[i])
        bit_m[i] = 0 if temp % 2 == 0 else 1
    
    if plot_bit:
        showBitSeq(bit_m, "Mouse Bit Sequence")
    
    return bit_m


def collectKeyboardEntropy(plot_bit=True, seconds=20):
    key_times = []
    
    def on_press(key):
        key_times.append(time.time())

    print("Type randomly on the keyboard...\n")
    time.sleep(2)
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    time.sleep(seconds)
    listener.stop()
    
    bit_k = np.zeros(shape=(len(key_times)))
    for i in range(len(key_times)):
        micro_sec = int(key_times[i] * 1000000)
        bit_k[i] = 0 if micro_sec % 2 == 0 else 1

    if plot_bit:
        showBitSeq(bit_k, "Keyboard Bit Sequence")

    return bit_k


def collectSystemEntropy(plot_bit=True, seconds=15):
    sys_bits = []
    print("Collecting entropy from the system noise...\n")
    t_end = time.time() + seconds
    
    while time.time() < t_end:
        c_stats = psutil.cpu_stats()
        n_stats = psutil.net_io_counters()
        d_stats = psutil.disk_io_counters()

        jitter = time.perf_counter_ns()
        raw_data = f"{c_stats.ctx_switches}{c_stats.interrupts}{n_stats.bytes_recv}{d_stats.read_bytes if d_stats else 0}{jitter}"
        hashed_val = hashlib.sha256(raw_data.encode()).digest()
        
        bit = hashed_val[-1] % 2
        sys_bits.append(bit)
        
        time.sleep(0.005)
    
    bit_s = np.array(sys_bits)

    if plot_bit:
        showBitSeq(bit_s, "System Bit Sequence")

    return bit_s