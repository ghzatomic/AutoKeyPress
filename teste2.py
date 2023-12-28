#you will need the win32 libraries for this snippet of code to work, Links below
import pyautogui
import pydirectinput
import sys
import time
import keyboard
import mouse
import threading


def grava():
    mouse_events = []
    keyboard_events = []


#    mouse.hook(mouse_events.append)
    keyboard.start_recording()

    keyboard.wait("f2")

#    mouse.unhook(mouse_events.append)
    keyboard_events = keyboard.stop_recording()
    return keyboard_events
    #Keyboard threadings:
    

    #k_thread = threading.Thread(target = lambda :keyboard.play(keyboard_events))
    #k_thread.start()

    #Mouse threadings:

#    m_thread = threading.Thread(target = lambda :mouse.play(mouse_events))
#    m_thread.start()

    #waiting for both threadings to be completed

#    k_thread.join() 
#    m_thread.join()

def xrange(x):
    return iter(range(x))

def main():
    #keyboard_events = grava()
    keyboard_events = [keyboard.KeyboardEvent("down",17,"w")]
    while(True):
        print(keyboard_events)
        keyboard.play(keyboard_events)
        for i in xrange(1):
            print(str(i)+' ')
            time.sleep(1)

if __name__ == "__main__":
    main()