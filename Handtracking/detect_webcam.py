import cv2
import mediapipe as mp
import subprocess
import os

# Configurar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Inicializar a câmera
camera = cv2.VideoCapture(0)
resolution_x = 1280
resolution_y = 720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_x)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_y)

notepad_process = None
mspaint_process = None
calc_process = None
google_opened = False

# Inicializar o módulo Hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

# Função para encontrar coordenadas das mãos
def find_coord_hand(img, side_inverted=False):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)
    all_hands = []

    # Desenhar landmarks se houver mãos detectadas
    if result.multi_hand_landmarks:
        for hand_side, hand_landmarks in zip(result.multi_handedness, result.multi_hand_landmarks):
            hand_info = {}
            coords = []
            for mark in hand_landmarks.landmark:
                coord_x = int(mark.x * resolution_x)
                coord_y = int(mark.y * resolution_y)
                coord_z = int(mark.z * resolution_x)
                coords.append((coord_x, coord_y, coord_z))

            if side_inverted:
                if hand_side.classification[0].label == "Left":
                    hand_info["side"] = "Right"
                else:
                    hand_info["side"] = " Left"
            else:
                    hand_info["side"] = hand_side.classification[0].label

                #print(hand_side.classification[0].label)
            hand_info["coordenadas"] = coords
            all_hands.append(hand_info)

            # Desenhar landmarks na imagem
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    return img, all_hands

def start_program(program):
    if program == "google":
        os.system("start https://www.google.com")
    else:
        return subprocess.Popen(program, shell=True)

def close_program(process_name):
    os.system(f"TASKKILL /IM {process_name} /F")

def fingers_raised(hand):
    fingers = []
    for fingertip in [8, 12, 16, 20]:
        if hand["coordenadas"][fingertip][1] < hand["coordenadas"][fingertip-2][1]:
            fingers.append(True)
        else:
            fingers.append(False)
    return fingers

# Loop principal
while camera.isOpened():
    ret, frame = camera.read()
    frame = cv2.flip(frame, 1)
    if not ret:
        print("Erro ao capturar o frame")
        break

    # Detectar e processar mãos
    img, all_hands = find_coord_hand(frame)
    if len(all_hands) == 1:
        info_finger_hand = fingers_raised(all_hands[0])
        if info_finger_hand == [True, False, False, True]:
            break
        elif info_finger_hand == [True, False, False, False] and google_opened is False:
            start_program("start https://www.linkedin.com/in/lucas-abner-caixeta/")  # Corrigido para abrir o Google
            google_opened = True  # Marca como já aberto

        elif info_finger_hand == [True, True, False, False] and mspaint_process is None:
            mspaint_process = start_program("mspaint")
        elif info_finger_hand == [True, True, True, False] and calc_process is None:
            calc_process = start_program("calc")
        elif info_finger_hand == [False, False, False, False]:
            if google_opened is not False:
                close_program("msedge.exe")
                google_opened = False
            elif calc_process is not None:
                close_program("CalculatorApp.exe")
                calc_process = None
            elif mspaint_process is not None:
                close_program("mspaint.exe")
                mspaint_process = None

    # Exibir a imagem
    cv2.imshow("Camera", img)
    key = cv2.waitKey(1)

    # Sair ao pressionar ESC
    if key == 27:
        break
   
# Liberar recursos
camera.release()
cv2.destroyAllWindows()
