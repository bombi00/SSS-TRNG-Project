from pynput import keyboard
import psutil

def on_press(key):
    try:
        print('Tasto alfanumerico {0} premuto'.format(key.char))
    except AttributeError:
        print('Tasto speciale {0} premuto'.format(key))
    if key == keyboard.Key.space:
        print('')
        return False

def on_release(key):
    if key == keyboard.Key.space:
        return
        
    print('{0} rilasciato'.format(key))

def prog():
    print("--------------------------")
    print("Choose your program:")
    print("--------------------------")
    print("1. Input from the keyboard \n2. Input from the mouse")
    if int(input()) == 1:
        print("press space to end the program")
        with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
            listener.join()
    else:
        return

mem_used = psutil.virtual_memory().used
print(mem_used)
prog()

