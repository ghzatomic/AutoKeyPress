#you will need the win32 libraries for this snippet of code to work, Links below

from win32.win32gui import *
from win32.win32api import PostMessage, keybd_event
from win32con import *
from time import sleep
from pick import pick


telas = {}

def winEnumHandler( hwnd, ctx ):
    if IsWindowVisible( hwnd ):
        title = GetWindowText( hwnd )
        hexdata = hex( hwnd )
        if title and title != "":
            telas[title] = hexdata

def show_drop():

    title = 'Escolha a tela: '
    options = ['Java', 'JavaScript', 'Python', 'PHP', 'C++', 'Erlang', 'Haskell']

    option, index = pick(options, title, indicator='=>', default_index=2)

def list_window_names():
    def winEnumHandler(hwnd, ctx):
        if IsWindowVisible(hwnd):
            print(hex(hwnd), '"' + GetWindowText(hwnd) + '"')
    EnumWindows(winEnumHandler, None)


def get_inner_windows(whndl):
    def callback(hwnd, hwnds):
        if IsWindowVisible(hwnd) and IsWindowEnabled(hwnd):
            hwnds[GetClassName(hwnd)] = hwnd
        return True
    hwnds = {}
    EnumChildWindows(whndl, callback, hwnds)
    return hwnds


def main():
    EnumWindows( winEnumHandler, None )

    #[hwnd] No matter what people tell you, this is the handle meaning unique ID, 
    #["Notepad"] This is the application main/parent name, an easy way to check for examples is in Task Manager
    #["test - Notepad"] This is the application sub/child name, an easy way to check for examples is in Task Manager clicking dropdown arrow
    #hwndMain = win32gui.FindWindow("Notepad", "test - Notepad") this returns the main/parent Unique ID
    
    # hwndMain = FindWindow("Notepad", "test - Notepad")

    #["hwndMain"] this is the main/parent Unique ID used to get the sub/child Unique ID
    #[win32con.GW_CHILD] I havent tested it full, but this DOES get a sub/child Unique ID, if there are multiple you'd have too loop through it, or look for other documention, or i may edit this at some point ;)
    #hwndChild = win32gui.GetWindow(hwndMain, win32con.GW_CHILD) this returns the sub/child Unique ID
    print(telas.keys())
    roblox_tela = list(filter(lambda x : "Roblox" == x, telas.keys()))
    if not roblox_tela or len(roblox_tela) == 0:
        print("NAO ACHOU ROBLOX")
        return 
    hwndMain = FindWindow(None, roblox_tela[0])

    ShowWindow(hwndMain, SW_MINIMIZE)
    sleep(1)  
    ShowWindow(hwndMain, SW_RESTORE)
    SetForegroundWindow(hwndMain)

    #hwndChild = GetWindow(int(telas[roblox_tela[0]]), GW_CHILD)

    #hwndMain = get_inner_windows(hwndMain)[list(get_inner_windows(hwndMain).keys())[0]]

    print(hwndMain) #you can use this to see main/parent Unique ID

    #SendMessage(hwndMain, WM_CHAR, 0x41, 0)

    #keybd_event(0x57, 0, 0, 0)  # Simula a tecla "W" pressionada
    #sleep(1)  # Aguarde 1 segundo (hipotético, ajuste conforme necessário)     
    #keybd_event(0x57, 0, KEYEVENTF_KEYUP, 0)  # Simula a tecla "W" liberada

    #PostMessage(hwndMain, WM_CLOSE, 0, 0)

    texto = "wwwww    dddddd"

    while(True):

        SendMessage(hwndMain, WM_KEYDOWN, VK_SPACE, 0)
        sleep(1)
        SendMessage(hwndMwin, WM_KEYDOWN, VK_SPACE, 0)
        
        PostMessage(hwndMain, WM_CHAR, VK_SPACE, 0)
        #[hwndChild] this is the Unique ID of the sub/child application/proccess
        #[win32con.WM_CHAR] This sets what PostMessage Expects for input theres KeyDown and KeyUp as well
        #[0x44] hex code for D
        #[0]No clue, good luck!
        #temp = win32api.PostMessage(hwndChild, win32con.WM_CHAR, 0x44, 0) returns key sent
        #temp = PostMessage(hwndMain, WM_CHAR, 0x41, 0)

        #print(temp) prints the returned value of temp, into the console
        #print(temp)
        #sleep(1) this waits 1 second before looping through again

if __name__ == "__main__":
    main()