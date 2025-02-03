from controla.controles import *
from controla.ossuario import *
from controla.mount_petram import *
from assist_connector import UOAssistConnector

def input_boolean(prompt="Deseja continuar? (s/n): "):
    while True:
        resposta = input(prompt).strip().lower()
        if resposta in ["s", "sim"]:
            return True
        elif resposta in ["n", "nao", "não"]:
            return False
        else:
            print("❌ Entrada inválida! Digite 's' para Sim ou 'n' para Não.")

if __name__ == "__main__":
    pause_flag = False
    print("1. Gravar movimentos")
    print("2. Reproduzir movimentos")
    print("3. Movimentos Randomicos")
    print("4. Movimentos Quadrados")
    print("5. Rodadinha")
    print("6. Movimento eldrich (5595 2865 -70) Mount Petram lvl2")
    print("7. Movimento batedor salinha ossuary melee")
    print("8. Movimento batedor salinha ossuary arco")
    print("9. Movimento batedor petram lvl2")
    print("10. Movimento batedor petram lvl1 Harpias")
    print("11. Movimento batedor petram lvl1 Earth elemental ")
    print("99. Gravar posições ")
    print("100. Ler posições ")
    choice = input("Escolha uma opção: ")

    if choice == "1":
        record_movements()  # Grava movimentos até pressionar F2
    elif choice == "2":
        replay_movements(input_file="movements.txt", return_to_origin_flag=True)
    elif choice == "3":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        perform_random_movements_with_breaks(
            num_movements=50, 
            delay=0.2, 
            pause_duration=60, 
            pause_interval=10
        )
    elif choice == "4":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        while True:
            perform_square_movements(duration=4, delay=1)
            random_sleep(1*60, 2*60)
            for x in range(10):
                clica_loot()
    elif choice == "5":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        while True:
            perform_random_movements(num_movements=2,delay=0.1,performBack=False)
            random_sleep(5, 6)
    elif choice == "6":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        while True:
            movimento_eldrich_sobe_desce()
            random_sleep(4*60, 10*60)
            #time.sleep(4*60)
    elif choice == "7":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        movimento_batedor_ossuario_salinha()
    elif choice == "8":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        movimento_batedor_ossuario_salinha_arco()
    elif choice == "9":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        movimento_batedor_petran_lvl2_dragoes_arco()
    elif choice == "10":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        movimento_batedor_petran_lvl1_harpia()
    elif choice == "11":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        movimento_batedor_petran_lvl1_earths()
    elif choice == "98":
        print("Iniciando "+choice+" - Va para a tela")
        time.sleep(3)
        uo_assist = UOAssistConnector()
    
        # Executar como administrador
        uo_assist.run_as_admin()

        # Conectar ao UOAssist
        if uo_assist.attach_to_assistant():
            # Obter coordenadas
            coords = uo_assist.get_character_coords()
            
        def delay_variavel():
            return random.uniform(0.2, 0.3)
        
        def on_move_log(x, y, target_x, target_y):
            print(f"Personagem se movendo... Atual: ({x}, {y}) -> Destino: ({target_x}, {target_y})")

        path = [
            (2165, 599, delay_variavel, on_move_log), 
            (2164, 653, delay_variavel, on_move_log), 
            (2178, 656, delay_variavel, on_move_log), 
            (2245, 699, delay_variavel, on_move_log), 
            (2225, 769, delay_variavel, on_move_log), 
        ]

        execute_movement_path(
            uo_assist=uo_assist,
            path=path,
            tolerance=2,  # Aceita uma variação de até 2 tiles no X e Y
            stuck_threshold=4  # Considera que está preso se repetir 4 vezes a mesma posição
        )
    elif choice == "99":
        uo_assist = UOAssistConnector()
    
        # Executar como administrador
        uo_assist.run_as_admin()

        # Conectar ao UOAssist
        if uo_assist.attach_to_assistant():
            # Obter coordenadas
            coords = uo_assist.get_character_coords()

        record_position_xy(uo_assist)
    
    elif choice == "100":
        uo_assist = UOAssistConnector()
    
        # Executar como administrador
        uo_assist.run_as_admin()

        # Conectar ao UOAssist
        if uo_assist.attach_to_assistant():
            # Obter coordenadas
            coords = uo_assist.get_character_coords()

        def delay_variavel():
            return random.uniform(0.2, 0.3)
        
        def clica_loot_timer():
            clica_loot(qtde=10)
            random_sleep(0.1,0.2)
        
        def on_move_log():
            print(f"Personagem se moveu... ")

        def on_move_click():
            clica_loot_timer()
            random_sleep(0.5,0.7)
        
        resposta_click = input_boolean("Você quer ativar o modo de click ? (s/n): ")
        resposta_click_loop = input_boolean("Você quer o macro em loop ? (s/n): ")

        move_callback_before = on_move_click if resposta_click else on_move_log
        move_callback_after = on_move_click if resposta_click else on_move_log

        path = load_movement_path_with_selection(move_callback_after=move_callback_after, move_callback_before=move_callback_before)
        if path:
            if resposta_click_loop:
                while True:
                    print("Iniciando "+choice+" - Va para a tela")
                    time.sleep(3)
                    execute_movement_path(uo_assist, path,stuck_threshold=2,tolerance=1) 
            else:
                print("Iniciando "+choice+" - Va para a tela")
                time.sleep(3)
                execute_movement_path(uo_assist, path,stuck_threshold=2,tolerance=1)
    else:
        print("Opção inválida!")