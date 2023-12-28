from ahk import AHK
from time import sleep

ahk = AHK()


def main():

    win = None # = ahk.win_get(title='Roblox')  # by title
    #all_windows = ahk.list_windows()               # list of all windows
    #win = ahk.win_get_from_mouse_position()        # the window under the mouse cursor
    #win = ahk.win_get(title='ahk_pid 20366')       # get window from pid

    try:
        # wait up to 5 seconds for notepad
        win = ahk.win_wait(title='Roblox', timeout=5)
        # see also: win_wait_active, win_wait_not_active
    except TimeoutError:
        print('Roblox was not found!')

    win.activate()
    sleep(1)
    win.minimize()

if __name__ == "__main__":
    main()