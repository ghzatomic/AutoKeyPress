import time
import vgamepad as vg

class GamepadController:
    def __init__(self):
        # Cria uma instância do controle Xbox 360 virtual
        self.gamepad = vg.VX360Gamepad()

        # Dicionário com seus movimentos
        self.movements = {
            'UP': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            'DOWN': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            'LEFT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            'RIGHT': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            'DIAGONAL_CIMA_DIREITA': [
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT
            ],
            'DIAGONAL_CIMA_ESQUERDA': [
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT
            ],
            'DIAGONAL_BAIXO_ESQUERDA': [
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT
            ],
            'DIAGONAL_BAIXO_DIREITA': [
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
                vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT
            ],
            'CLICKB': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            'CLICKA': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            'CLICKX': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            'CLICKY': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            'CLICKSTART': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            'CLICKBACK': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            'CLICKGUIDE': vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
            'CLICKRSHOULDER': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            'CLICKLSHOULDER': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER
        }

    def get_movements(self):
        return self.movements

    def press_and_release(self, movement, delay_ini=1, delay_end=None):
        """
        Pressiona e solta o botão definido em 'movement_key'.
        :param movement_key: Nome do movimento (chave do dicionário self.movements).
        :param delay_ini: Tempo em segundos para manter o botão pressionado.
        :param delay_end: Tempo em segundos para aguardar após soltar o botão.
        """
        #movement = self.movements.get(movement_key)
        if not movement:
            print(f"[Gamepad] Movimento '{movement}' não encontrado.")
            return

        # Pressiona o(s) botão(ões)
        if isinstance(movement, list):
            for m in movement:
                self.gamepad.press_button(m)
            self.gamepad.update()
        else:
            self.gamepad.press_button(movement)
            self.gamepad.update()

        # Segura o botão pressionado por 'delay_ini' segundos
        if delay_ini:
            time.sleep(delay_ini)

        # Solta o(s) botão(ões)
        if isinstance(movement, list):
            for m in movement:
                self.gamepad.release_button(m)
            self.gamepad.update()
        else:
            self.gamepad.release_button(movement)
            self.gamepad.update()

        # Espera mais 'delay_end' segundos antes de retornar
        if delay_end:
            time.sleep(delay_end)
