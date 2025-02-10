import time

import mss
from PIL import Image
import sys # Importa a biblioteca sys para pegar argumentos da linha de comando

def cortar_captcha_com_borda(imagem_path=None):
    """
    Detecta e corta a área do captcha com borda marrom de uma imagem (screenshot ou PNG).
    Salva a área cortada como 'captcha_com_borda_cortado.png'.

    Args:
        imagem_path (str, opcional): Caminho para um arquivo de imagem PNG.
                                     Se não fornecido, tira um print screen da tela.
    """
    if imagem_path:
        # Carrega a imagem do arquivo PNG fornecido
        try:
            img = Image.open(imagem_path).convert("RGB") # Converte para RGB para trabalhar com cores
            print(f"Imagem carregada do arquivo: {imagem_path}")
        except FileNotFoundError:
            print(f"Erro: Arquivo de imagem não encontrado: {imagem_path}")
            return
        except Exception as e:
            print(f"Erro ao abrir a imagem: {e}")
            return

    else:
        # Captura a tela inteira (se nenhum caminho de imagem for fornecido)
        with mss.mss() as sct:
            monitor = sct.monitors[1] # Pega o monitor principal (pode precisar ajustar se tiver múltiplos monitores)
            im = sct.grab(monitor)
            img = Image.frombytes("RGB", (im.width, im.height), im.raw, "raw", "RGB", 0, 1).convert("RGB") # Converte para RGB
            print("Screenshot da tela capturado.")

    largura, altura = img.size

    # *** Detecção da Borda Marrom ***
    cor_borda_marrom = (99, 74, 43)  # Cor marrom amostrada das imagens de captcha (pode precisar ajuste fino)
    tolerancia_cor = 50 # Tolerância para variação de cor (ajuste se necessário)

    min_x, min_y, max_x, max_y = largura, altura, 0, 0 # Inicializa com valores extremos

    encontrou_borda = False

    for x in range(largura):
        for y in range(altura):
            pixel_cor = img.getpixel((x, y))
            # Verifica se a cor do pixel está dentro da tolerância da cor marrom
            if (abs(pixel_cor[0] - cor_borda_marrom[0]) < tolerancia_cor and
                abs(pixel_cor[1] - cor_borda_marrom[1]) < tolerancia_cor and
                abs(pixel_cor[2] - cor_borda_marrom[2]) < tolerancia_cor):
                encontrou_borda = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if encontrou_borda:
        print("Borda marrom detectada.")
        margem = 10
        area_captcha_cortada = (max(0, min_x - margem), max(0, min_y - margem), min(largura, max_x + margem), min(altura, max_y + margem))

        captcha_crop_regiao = img.crop(area_captcha_cortada)
        largura_crop, altura_crop = captcha_crop_regiao.size # Obtém o tamanho do crop

        # *** Cria uma NOVA imagem com o tamanho do crop e cola a região recortada ***
        captcha_cortado = Image.new("RGB", (largura_crop, altura_crop))
        captcha_cortado.paste(captcha_crop_regiao, (0, 0)) # Cola no canto superior esquerdo

        # Salva a imagem cortada com o tamanho correto
        captcha_cortado.save("captcha_com_borda_cortado.png")
        print("Imagem do captcha com borda cortada e salva como 'captcha_com_borda_cortado.png'")

    else:
        print("Borda marrom não detectada na imagem.")
        print("Não foi possível cortar o captcha com borda.")
        # Salva a tela inteira para debug, se quiser
        # img.save("tela_inteira_borda_nao_detectada.png")

if __name__ == "__main__":
    # Se um argumento de linha de comando for passado, assume que é o caminho para a imagem PNG
    #imagem_path_input = "./image.png"
    #print(f"Processando imagem do arquivo: {imagem_path_input}")
    #cortar_captcha_dinamico(imagem_path_input)
    
    # Se nenhum argumento for passado, tira um print screen da tela
    print("Nenhum arquivo de imagem fornecido. Capturando screenshot da tela... ( 3 segundos e volte )")
    time.sleep(3)
    cortar_captcha_com_borda()