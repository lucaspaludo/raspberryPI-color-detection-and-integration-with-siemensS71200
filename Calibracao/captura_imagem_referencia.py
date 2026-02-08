import cv2
import os
import time

# Configurações da ROI
roi_x = 80
roi_y = 50
roi_w = 220
roi_h = 180

def capturar_fundo_referencia():
    # Caminho absoluto para a pasta 'Assets' na raiz do projeto
    raiz_projeto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pasta_assets = os.path.join(raiz_projeto, "Assets")
    salvar_em = os.path.join(pasta_assets, "camera_referencia.jpg")

    os.makedirs(pasta_assets, exist_ok=True)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    time.sleep(2)
    print("Pressione 's' para capturar, 'q' para sair.")

    window_name = "Captura de Referência"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            # Desenha o retângulo da ROI
            cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 255, 0), 2)

            # Texto verde, maior e com espessura aumentada
            cv2.putText(
                frame,
                "Alinhe e pressione 'Confirmar'",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,  # tamanho da fonte aumentado
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                cv2.imwrite(salvar_em, frame)
                print(f"Imagem salva em: {salvar_em}")
                break

            elif key == ord('q'):
                print("Saindo sem salvar.")
                break

    finally:
        cap.release()
        cv2.destroyWindow(window_name)

if __name__ == "__main__":
    capturar_fundo_referencia()
