import logging
from tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime, timedelta
import os
from pyzbar import pyzbar
import threading
import socket
import time
import json
import shutil
from ultralytics import YOLO
from tkinter.scrolledtext import ScrolledText
from tkinter import simpledialog

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(END)
        self.text_widget.after(0, append)

#variables
configuracion_default = 'variables.json'
modificable = 'config.json'
logger = logging.getLogger(__name__)
frame_comp = None

#copiar las variables default del .json
if os.path.exists(configuracion_default):
    shutil.copy(configuracion_default, modificable)

with open('config.json','r') as f:
    config =  json.load(f)

os.makedirs("/home/axel08/Desktop/proyect/loren/capturas", exist_ok=True)

Ultima_captura = {}
#classes con variables instanciadas
class globales():
    def __init__(self):
        #conexion
        self.sock = None
        self.conected = False
        #sensores
        self.file_qr = config["qr_file"]
        self.codigos_guardados = self.cargar_codigos_existentes(self.file_qr)
        self.hazmat_model = YOLO(config['ruta_modelo'])
        #widgets de pantalla
        self.pantalla = Tk()
        self.lblVideo = Label(self.pantalla)
        self.lblTrasera = Label(self.pantalla)  

    #sensores

    def deshabilitar_modos(self):
        config['sensor'] = 0
        slide.place_forget()

    #tracker
    def habilitar_tracker(self):
        config['sensor'] = 1
        slide.place(x=800,y=140)
        slide.place_info
    def aumentar_framecont(self):
        config['frame_count'] += 1
    #qr
    def habilitar_qr(self):
        config['sensor'] = 0
        slide.place_forget()
    
    def cargar_codigos_existentes(self,b):
        if not os.path.exists(b):
            return set()
        with open(b, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    
    #hazmat
    def habilitar_hazmat(self):
        config['sensor'] = 3
        slide.place_forget

    #conexion
    def cambiar_sock(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def encender_conected(self):
        self.conected = True
    def apagar_conected(self):
        self.conected = False
    def iniciar_recepcion(self):
        self.receptor = threading.Thread(target=recibir_datos, daemon=True, args=(self.sock,))
        self.receptor.start()
    
    #movimiento
    def aumentar_velocidad(self):
        if config['velocidad'] >1:
            config['velocidad'] -=1
    def reducir_velocidad(self):
        if config['velocidad'] <3:
            config['velocidad'] +=1

        
variable = globales()

class CameraHandler:
    def __init__(self, cam_index=0, name="Cam"):
        self.cam_index = cam_index
        self.name = name
        self.cap = None
        self.running = True
        self.connected = False
        self.reconnect_delay = 5  # segundos

        self._start_camera()

        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.reconnect_thread.start()

    def _start_camera(self):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_V4L2)
        self.connected = self.cap.isOpened()
        logger.debug(f"[{self.name}] Conectado: {self.connected}")

    def _reconnect_loop(self):
        while self.running:
            if not self.connected:
                logger.debug(f"[{self.name}] Intentando reconectar...")
                self._start_camera()
            time.sleep(self.reconnect_delay)

    def get_frame(self):
        if self.connected:
            ret, frame = self.cap.read()
            if not ret:
                logger.error(f"[{self.name}] Desconectada.")
                self.connected = False
                return None
            return frame
        return None

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()


def pedir_indices_camaras():

    root = Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    cam1 = simpledialog.askinteger("Cámara principal", "Ingresa el índice de la cámara principal (Cam1):", minvalue=0)
    cam2 = simpledialog.askinteger("Cámara secundaria", "Ingresa el índice de la cámara secundaria (Cam2):", minvalue=0)
    root.destroy()
    return cam1, cam2

#ajustar las camaras
cam_index1, cam_index2 = pedir_indices_camaras()
cap = CameraHandler(cam_index=cam_index1, name="Cam1")
cap2 = CameraHandler(cam_index=cam_index2, name="Cam2")
#conexion con el servidor
def conectarse_server():
    while True:
        if not variable.conected:
            try:
                variable.cambiar_sock()
                variable.sock.settimeout(5)
                variable.sock.connect((config['server_host'], config['comando_port']))
                variable.sock.setblocking(True)
                variable.encender_conected()
                logger.debug("[INFO] Conectado al servidor.")

                #inicia hilo de recepción
                variable.iniciar_recepcion()

            except Exception as e:
                variable.apagar_conected()
                logger.warning(f"[REINTENTO] No se pudo conectar: {e}")
        time.sleep(3)


def enviar_comandos(comando):
    if not variable.conected:
        return
    try:
        mensaje = str(comando).encode('utf-8')
        variable.sock.sendall(mensaje)
    except Exception as e:
        logger.error(f"[ERROR envío comando]: {e}")
        variable.apagar_conected()

def recibir_datos(socket_cliente):
    try:
        while variable.conected:
            data = socket_cliente.recv(1024).decode()
            if not data:
                logger.warning("[DESCONECTADO] El servidor cerró la conexión.")
                break
            logger.debug(f"[DATA] Temperatura recibida: {data.strip()}")

    except Exception as e:
        logger.error(f"[ERROR RECEPCIÓN] {e}")

    finally:
        try:
            socket_cliente.close()
        except:
            pass
        variable.apagar_conected()
        logger.warning("[RECONEXIÓN] Esperando para reconectar...")

hilo_comunicacion = threading.Thread(target=conectarse_server, daemon = True)
hilo_comunicacion.start()

#capturas de pantalla
def capturar_pantalla():
    if cap is not None:
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ruta = os.path.join("capturas", f"captura_{fecha_hora}.jpg")
        os.makedirs("capturas", exist_ok=True)
        cv2.imwrite(ruta, frame)
        logger.debug(f"[INFO] Captura guardada en: {ruta}")

#cambiar la pantalla completa
def toggle_fullscreen(event=None):
    variable.pantalla.attributes('-fullscreen', not variable.pantalla.attributes('-fullscreen'))

def exit_fullscreen(event=None):
    variable.pantalla.attributes('-fullscreen', False)
#evento de teclas
teclas_presionadas = set()
def tecla_presionada(event):
    tecla = event.keysym.lower()
    
    teclas_ignoradas = {
        'shift_r', 'control_r', 'alt_l', 'alt_r',
        'caps_lock', 'num_lock', 'scroll_lock',
        'escape', 'tab', 'return',
        'insert', 'delete', 'home', 'end',
        'prior', 'next', 'f1', 'f2', 'f3', 'f4',
        'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
        'f11', 'f12'
    }

    if tecla in teclas_ignoradas:
        return

    if tecla not in teclas_presionadas:
        teclas_presionadas.add(tecla)
        logger.debug(f"Presionada: {tecla}")

        #acciones inmediatas al presionar
        acciones = {
            '1': lambda: variable.habilitar_tracker(),
            '2': lambda: variable.habilitar_qr(),
            '3': lambda: cambio(),
            '0': lambda: variable.deshabilitar_modos(),
            '4': lambda: capturar_pantalla(),
            '5': lambda: variable.habilitar_hazmat(),
            'shift_l': lambda: variable.aumentar_velocidad(),
            'control_l': lambda: variable.reducir_velocidad()
        }
        if tecla in acciones:
            acciones[tecla]()

def tecla_liberada(event):
    tecla = event.keysym.lower()
    if tecla in teclas_presionadas:
        teclas_presionadas.remove(tecla)
        logger.info(f"Soltada: {tecla}")
    
    # Solo envía "b,0" si NO queda ninguna tecla presionada
    if not teclas_presionadas:
        enviar_comandos("b,0")


def envio_periodico():
    while True:
        for tecla in list(teclas_presionadas):
            enviar_comandos(f"{tecla},{config['velocidad']}")
        time.sleep(0.1)

threading.Thread(target=envio_periodico, daemon=True).start()


#tracker
def trackerMov(frame1, frame2, frame):
    if frame1 is None or frame2 is None:
        return frame
    sens = slide.get()
    kernel = np.ones((5, 5), np.uint8)
    if frame1.shape != frame2.shape:
        frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
    diff = cv2.subtract(frame2, frame1)
    _, thresh = cv2.threshold(diff, sens, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    cnts, res = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in cnts:
        if 10 < cv2.contourArea(contour) < 500:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return frame

def to_gray(image):
    if image is None:
        return None
    if len(image.shape) == 3 and image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

#Qr
def qr(frameqr):
    detection = pyzbar.decode(frameqr)
    
    for i in range(len(detection)):
        x, y, w, h = detection[i].rect
        cv2.rectangle(frameqr, (x, y), (x + w, y + h), (255, 0, 0), 2)
        text = detection[i].data.decode("utf-8")
        cv2.putText(frameqr, text, (x, y - 10), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)

        if text not in variable.codigos_guardados:
            with open(variable.file_qr, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            variable.codigos_guardados.add(text)
    if len(detection) >= 8:
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cv2.imwrite(f"detections_qr/{fecha_hora}.jpg", frameqr)

#Hazmat
def detectar_hazmat(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = variable.hazmat_model.predict(rgb_frame, conf=0.7, verbose=False)

    if not results:
        return

    result = results[0]
    boxes = result.boxes
    names = result.names

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = float(box.conf[0])
        label = names[int(box.cls[0])]
        
        #solo guardar si la confianza es muy alta
        if conf > 0.8:
            ahora = datetime.now()
            ultima = Ultima_captura.get(label, ahora - timedelta(seconds=10))

            if (ahora - ultima).total_seconds() >= 5:
                filename = os.path.join("/home/axel08/Desktop/proyect/loren/capturas", f"hazmat_{label}_{ahora.strftime('%Y%m%d_%H%M%S')}.jpg")
                cv2.imwrite(filename, frame)
                Ultima_captura[label] = ahora  #actualizar última captura

        #dibuja rectángulo y etiqueta
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)


#desempaquetar las camaras
def cambio():
    global cap, cap2
    cap,cap2 = cap2,cap

#ambas camaras puestas en tkinter   
#camara principal con sus respectivos filtros
def Loop():
    global frame_comp, frame
    if cap is not None:
        frame = cap.get_frame()
        if frame is None:
            lblVideo.after(15, Loop)
            return

        if config['sensor'] == 2:
            qr(frame)

        if config['sensor'] == 1:
            variable.aumentar_framecont()
            if config['frame_count'] % 5 == 0:
                frame_comp = frame.copy()
            gray1 = to_gray(frame_comp)
            gray = to_gray(frame)
            trackerMov(gray, gray1, frame)
        
        elif config['sensor'] == 3:
            detectar_hazmat(frame)

        first = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        first = cv2.resize(first, (810, 780))
        im = Image.fromarray(first)
        img = ImageTk.PhotoImage(image=im)

        lblVideo.configure(image=img)
        lblVideo.image = img
        lblVideo.after(15, Loop)

#camara secundaria que no contienen filtros
def trasera():
    global frame_comp, lblTrasera

    if cap2 is not None:
        frame2 = cap2.get_frame()
        if frame2 is None:
            lblTrasera.after(60, trasera)
            return

        first = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
        first = cv2.resize(first, (560, 310))
        im = Image.fromarray(first)
        img = ImageTk.PhotoImage(image=im)

        lblTrasera.configure(image=img)
        lblTrasera.image = img
        lblTrasera.after(60, trasera)


#Interfaz Tkinter
def run():
    global lblVideo, slide, lblTrasera
    variable.pantalla.title("Cloud Interface")
    variable.pantalla.geometry("1366x786")

    imagenF = Image.open("cloud.jpg")
    imagenF = imagenF.resize((1366, 768), Image.LANCZOS)
    imagenF_tk = ImageTk.PhotoImage(imagenF)
    background = Label(variable.pantalla, image=imagenF_tk)
    background.image = imagenF_tk
    background.place(x=0, y=0)

    lblVideo = Label(variable.pantalla)
    lblVideo.place(x=0, y=0)

    lblTrasera = Label(variable.pantalla)
    lblTrasera.place(x=810, y=460)

    slide = Scale(variable.pantalla, from_=10, to=130, orient=VERTICAL)

    #bindings para teclas
    variable.pantalla.bind("<KeyPress>", tecla_presionada)
    variable.pantalla.bind("<KeyRelease>", tecla_liberada)
    variable.pantalla.bind("<9>", toggle_fullscreen) 
    variable.pantalla.bind("<8>", exit_fullscreen)

    variable.pantalla.focus_force()

    #consola de logs en la GUI
    log_console = ScrolledText(variable.pantalla, height=8, width=70, bg='black', fg='white', state='disabled')
    log_console.place(x=810, y=0)  # Puedes ajustar esta posición

    #crear handler del logger para el widget
    text_handler = TextHandler(log_console)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    text_handler.setFormatter(formatter)

    #configurar logger
    logger.setLevel(logging.DEBUG)  # Cambia a INFO o WARNING si quieres menos detalle
    logger.addHandler(text_handler)

    Loop()
    trasera()
    variable.pantalla.mainloop()
