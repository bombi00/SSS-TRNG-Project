import time
from pynput import mouse
import matplotlib.pyplot as plt
import numpy as np

def showMousePositions(x,y):
    plt.figure(figsize=(16, 9))
    plt.scatter(x, y, s=1)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Mouse positions")
    plt.show()

def showMouseBitSeq(seq):
    plt.figure(figsize=(20, 4))
    plt.plot(range(len(seq)), seq)
    plt.ylim(-0.2, 1.2)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("Bit sequence")
    plt.grid(True)
    plt.show()

def collectMouseEntropy(plot_mouse = True, plot_bit = True, seconds = 15):
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
        time.sleep(0.01)

    if plot_mouse == True:
        showMousePositions(x_coo, y_coo)
    
    bit_m = np.zeros(shape=(len(x_coo)))
    for i in range(len(x_coo)):
        temp = int(x_coo[i] + y_coo[i])
        bit_m[i] = 0 if temp % 2 == 0 else 1
    
    if plot_bit == True:
        showMouseBitSeq(bit_m)
    
    return bit_m

def collect_keyboard_entropy(plot_keyboard = True, seconds = 15):
    
    
    return 1

