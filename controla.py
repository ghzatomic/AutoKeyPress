from controla.controles import *
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
    print("1. Gravar posições ")
    print("2. Ler posições ")
    choice = input("Escolha uma opção: ")
    
    if choice == "1":
        uo_assist = UOAssistConnector()
    
        # Executar como administrador
        uo_assist.run_as_admin()

        # Conectar ao UOAssist
        if uo_assist.attach_to_assistant():
            # Obter coordenadas
            coords = uo_assist.get_character_coords()

        record_position_xy(uo_assist)
    
    elif choice == "2":
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
                    execute_movement_path(uo_assist, path,stuck_threshold=5,tolerance=1) 
            else:
                print("Iniciando "+choice+" - Va para a tela")
                time.sleep(3)
                execute_movement_path(uo_assist, path,stuck_threshold=5,tolerance=1)
    else:
        print("Opção inválida!")