import pygetwindow as gw
import time
import keyboard
import pydirectinput
from pywinauto import application
from pywinauto.keyboard import SendKeys

def main():

    # Encontre ou inicie a aplicação
    app = application.connect(title="Roblox")

    # Selecione a janela específica
    window = app.window(title="Roblox")

    # Envie a sequência de caracteres para a janela em segundo plano
    texto = "wwwwwwwwwwwww"
    window.type_keys(texto)


if __name__ == "__main__":
    main()