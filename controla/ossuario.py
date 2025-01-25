from controla.controles import *



def perform_square_movements_batedor_ossuario(duration=1, delay=0.5):
    """
    Realiza movimentos em formato de quadrado por uma duração especificada.
    
    Args:
        duration (float): Duração total para os movimentos, em segundos.
        delay (float): Tempo de espera entre as ações, em segundos.
    """
    print("Iniciando movimentos em quadrado...")
    start_time = time.time()
    square_sequence = ['UP', 'RIGHT', 'DOWN', 'LEFT','UP']  # Sequência de movimentos

    while time.time() - start_time < duration:
        for move in square_sequence:
            # Simula o movimento no gamepad
            pressiona_botao(movements[move],delay_ini=delay)

    print("Finalizado! Movimentos em quadrado completos.")

def perform_square_sobedesce_batedor_ossuario(delay=3, delay_between_buttons=None,func_beteen_moves=None):
    """
    Realiza movimentos em formato de quadrado por uma duração especificada.

    Args:
        delay (float): Tempo total para os movimentos, em segundos.
        delay_between_buttons (float): Tempo entre as ações individuais, em segundos.
    """
    print("Iniciando movimentos em diagonal...")
    square_sequence = ['UP', 'DOWN', 'UP']  # Sequência de movimentos

    if delay_between_buttons:
        # Calcula o número de execuções com base no delay total
        num_executions = int(delay / delay_between_buttons)

        for move in square_sequence:
            for _ in range(num_executions):
                pressiona_botao(movements[move], delay_ini=delay_between_buttons)
                time.sleep(delay_between_buttons)
                if func_beteen_moves:
                    func_beteen_moves()
    else:
        for move in square_sequence:
            pressiona_botao(movements[move], delay_ini=delay)
            if func_beteen_moves:
                func_beteen_moves()

    print("Finalizado! Movimentos em diagonal completos.")

def movimento_batedor_ossuario_salinha():
    while True:
        perform_square_movements_batedor_ossuario(duration=8,delay=1)
        
        random_sleep(60, 2*60)
        for x in range(10):
            clica_loot()
            random_sleep(1, 1)
        perform_random_movements_with_breaks(
            num_movements=3, 
            delay=0.3, 
            pause_duration=0, 
            pause_interval=0.6
        )
        for x in range(10):
            clica_loot()
            random_sleep(1, 1)
        perform_square_sobedesce_batedor_ossuario(delay=4)
        random_sleep(80, 3*60)
        for x in range(10):
            clica_loot()
            random_sleep(1, 1)
        perform_random_movements_with_breaks(
            num_movements=4, 
            delay=0.3, 
            pause_duration=0, 
            pause_interval=0.6
        )
        for x in range(10):
            clica_loot()
            random_sleep(1, 1)

def movimento_batedor_ossuario_salinha_arco():
    delay_cait = 0.6

    def clica_loot_timer():
        clica_loot()
        random_sleep(0.1,0.1)

    def resetar_salinha():

        sequence = [
            ('UP',delay_cait), ('LEFT',delay_cait), ('DOWN',0.3),('LEFT',delay_cait),
            ('LEFT',delay_cait), ('UP',delay_cait), ('RIGHT',delay_cait),
            ('UP',delay_cait),('UP',delay_cait), ('LEFT',delay_cait), ('UP',delay_cait), ('UP',delay_cait),
            ('RIGHT',delay_cait), ('UP',delay_cait), ('LEFT',delay_cait), ('UP',delay_cait),('UP',delay_cait),('UP',delay_cait)
        ]  # Sequência de movimentos

        for move,delay in sequence:
            print(f"Aqui : {move},{delay}")
            pressiona_botao(movements[move], delay_ini=delay)
            time.sleep(delay_cait)
            clica_loot_timer()
            #for x in range(2):
            #    clica_loot()

    while True:
        #RESETAR
        resetar_salinha()
        random_sleep(1,15)
        for x in range(8):
            perform_random_movements_with_breaks(
                num_movements=2, 
                delay=0.3, 
                pause_duration=0, 
                pause_interval=delay_cait,
                func_beteen_moves=clica_loot_timer,
                move_keys = ['RIGHT', 'DOWN', 'LEFT'],
            )
            for x in range(2):
                clica_loot_timer()
            random_sleep(1,15)
        perform_square_sobedesce_batedor_ossuario(delay=5,delay_between_buttons=1,
                func_beteen_moves=clica_loot_timer)
        random_sleep(1,15)