import pygetwindow as gw
import time
import keyboard
import pydirectinput

def main():


    roblox_window = gw.getWindowsWithTitle("Roblox")[0]
    roblox_window.activate()
    time.sleep(5)
    # Execute outras ações conforme necessário
    # Por exemplo, você pode simular cliques do mouse com o 'mouse.click()' do módulo 'mouse'

    # Mantenha o programa em execução para manter a automação em segundo plano
    while True:
        # Simule a pressionamento da tecla "W" (frente) no teclado
        pydirectinput.keyDown('f')
        time.sleep(2) 
        pydirectinput.keyUp('f')
        time.sleep(2) 
        # Mantém a tecla spressionada p3orss 2 segundos
if __name__ == "__main__":
    main()