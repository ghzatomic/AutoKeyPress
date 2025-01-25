from controla.controles import *
from controla.ossuario import *
from controla.mount_petram import *



if __name__ == "__main__":
    print("1. Gravar movimentos")
    print("2. Reproduzir movimentos")
    print("3. Movimentos Randomicos")
    print("4. Movimentos Quadrados")
    print("5. Rodadinha")
    print("6. Movimento eldrich")
    print("7. Movimento batedor salinha melee")
    print("8. Movimento batedor salinha arco")
    print("9. Movimento batedor petram arco")
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
        perform_square_movements(duration=1, delay=0.3)
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
    else:
        print("Opção inválida!")