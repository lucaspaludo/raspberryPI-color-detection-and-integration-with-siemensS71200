import tkinter as tk
import cv2
from PIL import Image, ImageTk
import numpy as np
from tkinter import messagebox
from CameraManager.camera_manager import CameraManager
import os


class TelaCalibracao:
    def __init__(self, camera, parent, voltar_callback):
              
        self.root = tk.Toplevel(parent)
        self.root.transient(parent)
        self.root.grab_set()
        self.root.focus_force()
        self.voltar_callback = voltar_callback
        self.root.protocol("WM_DELETE_WINDOW", self.voltar)
        
                              
        self.root.title("Calibração")
        self.root.geometry("500x350")
        self.root.configure(bg="#121220")
        
        self.label = tk.Label(self.root, bg="#121220")
        self.label.pack(pady=10)
        
        self.camera = camera
        self.voltar_callback = voltar_callback
        
        raiz_projeto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        caminho_ref = os.path.join(raiz_projeto, "Assets", "camera_referencia.jpg")
        self.alpha = 0.5
       
        
        if os.path.exists(caminho_ref):
                self.fundo_ref = cv2.imread(caminho_ref)
                self.fundo_ref = cv2.resize(self.fundo_ref, (320, 240))
        else:
                self.fundo_ref = np.zeros((240, 320, 3), dtype=np.uint8)
                    
        btn_voltar = tk.Button(self.root, text="Confirmar", command=self.voltar, cursor="hand2")
        btn_voltar.pack(pady=10)

        self.atualizar_video()

    def atualizar_video(self):
        frame = self.camera.get_frame()
        if frame is not None: 
            
            sobreposto = cv2.addWeighted(frame, self.alpha, self.fundo_ref, self.alpha, 0)
            
            
            imagem = cv2.cvtColor(sobreposto, cv2.COLOR_BGR2RGB)
            imagem = Image.fromarray(imagem)
            imagem = ImageTk.PhotoImage(imagem)
            self.label.imgtk= imagem
            self.label.configure(image=imagem)
        self.root.after(30, self.atualizar_video)

    def voltar(self):
        self.root.destroy()
        if self.voltar_callback:
                self.voltar_callback()

