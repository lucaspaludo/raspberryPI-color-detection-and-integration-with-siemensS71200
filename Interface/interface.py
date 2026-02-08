import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ProcessaImagem.processaImagem import ProcessaImagem
from Calibracao.calibracao import TelaCalibracao
import cv2
import time
from ModbusTCP.modbusTCP import ModbusTCP
import threading
from S7.s7 import S7Client
from MQTT import mqtt
import os
from CameraManager.camera_manager import CameraManager

class Interface:
    def __init__(self, modbusTCP=None, mqtt=None):

        self.root = tk.Tk()
        self.camera = CameraManager()
        self.processo_imagem = ProcessaImagem(self.camera)
        self.servidor_modbus = ModbusTCP()
        self.servidor_s7 = S7Client()

        self.modbusTCP = modbusTCP
        self.atualizacao_continua = False
        self.thread_atualizacao = None
        self.mqtt = mqtt

        self.selected_protocol = tk.StringVar(value="")

        self.root.grid_rowconfigure((0,1,2), weight=1)
        self.root.grid_columnconfigure((0,1), weight=1)
        
        self.card_camera = self.create_card(self.root, "Visualização da Câmera")
        self.card_camera.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.video_label = tk.Label(self.card_camera, bg="#2C2C3C", width=320, height=240)
        self.video_label.pack(pady=10)

        self.ultima_cor_detectada = ""
        self.tempo_inicio_cor = None
        self.contagem_realizada = False

        self.threshold_preto = 40
        self.threshold_cromado = 20
        self.threshold_transparente = 30

        self.estado_atual_contagem = {
            "Vermelho": 0,
            "Preto": 0,
            "Cromado": 0,
            "Transparente": 0
        }

        self.contadores = {
            "Vermelho": 0,
            "Preto": 0,
            "Cromado": 0,
            "Transparente": 0,
        }

        style = ttk.Style(self.root)
        style.theme_use("clam")

 
        self.root.title("Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg="#121220")

        base_path = os.path.dirname(os.path.abspath(__file__))
        confirm_path = os.path.join(base_path, "confirm_icon.png")
        calibrate_path = os.path.join(base_path, "calibrate_icon.png")

        self.confirm_icon = ImageTk.PhotoImage(Image.open(confirm_path).resize((15, 15)))
        self.calibrate_icon = ImageTk.PhotoImage(Image.open(calibrate_path).resize((15, 15)))
        
        self.after_id = None

        self.create_layout()
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)
        self.after_id = None
        self.iniciar_camera()


    def iniciar_camera(self):
        
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        frame = self.processo_imagem.get_frame()

        if frame is not None:
            imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagem =  Image.fromarray(imagem)
            imagem = ImageTk.PhotoImage(imagem)
            self.video_label.imgtk = imagem
            self.video_label.configure(image=imagem)

            # Atualiza cor detectada
            cor_atual = self.processo_imagem.ultima_cor_detectada
            tempo_atual = time.time()

            if cor_atual:
                if cor_atual != self.ultima_cor_detectada:
                    self.ultima_cor_detectada = cor_atual
                    self.tempo_inicio_cor = tempo_atual
                    self.contagem_realizada = False
                else:
                    if not self.contagem_realizada and self.tempo_inicio_cor and (tempo_atual - self.tempo_inicio_cor >= 2):
                        self.contadores[cor_atual] += 1
                        self.estado_atual_contagem = dict(self.contadores)
                        self.dados_cores_atualizados = dict(self.contadores)

                        self.labels_contadores[cor_atual].config(text=f"{self.contadores[cor_atual]}")
                        self.enviar_dados_para_protocolo()
                        self.contagem_realizada = True
            else:
                self.ultima_cor_detectada = ""
                self.tempo_inicio_cor = None
                self.contagem_realizada = False

            if hasattr(self, "label_info_cor"):
                self.label_info_cor.config(text=f"Cor detectada: {cor_atual or 'Nenhuma'}")
        else:
            # fallback em caso de erro ou frame vazio
            erro_img = ImageTk.PhotoImage(Image.new('RGB', (320, 240), color='gray'))
            self.video_label.imgtk = erro_img
            self.video_label.configure(image=erro_img)
            
        

        self.after_id = self.root.after(30, self.iniciar_camera)


    def abrir_calibracao(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
            
        self.btn_confirmar.config(state="disabled", cursor="")
        self.btn_calibrar.config(state="disabled", cursor="")
        
        for slider, _ in self.sliders.values():
            slider.state(["disabled"])
            slider.configure(cursor="arrow")
            
            
        def voltar_callback():
            self.btn_confirmar.config(state="enabled", cursor="hand2")
            self.btn_calibrar.config(state="enabled", cursor="hand2")
            
            for slider, _ in self.sliders.values():
                slider.state(["!disabled"])
                slider.configure(cursor="hand2")
            self.after_id = self.root.after(30, self.iniciar_camera)
            
        TelaCalibracao(self.camera, self.root, voltar_callback)

    def fechar(self):
        self.camera.release()
        self.root.destroy()
    


    def create_card(self, parent, title):
        frame = tk.Frame(parent, bg="#1E1E2F", bd=0, highlightthickness=0)
        label = tk.Label(frame, text=title, fg="white", bg="#1E1E2F", font=("Segoe UI", 13, "bold"))
        label.pack(anchor="w", padx=10, pady=(10,5))
        return frame
    
    def create_layout(self):
      
        self.card_protocol = self.create_card(self.root, "Selecionar Protocolo")
        self.card_protocol.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for proto in ["Modbus/TCP", "S7", "MQTT"]:
            rb = ttk.Radiobutton(self.card_protocol, text=proto, value=proto, variable=self.selected_protocol, style="Custom.TRadiobutton", cursor="hand2")
            rb.pack(anchor="w", padx=10, pady=2)
        self.btn_confirmar = ttk.Button(self.card_protocol, text="  Confirmar", image=self.confirm_icon, compound="left", command=self.selecionaProtocolo, style="Rounded.TButton", cursor="hand2")
        self.btn_confirmar.pack(pady=10)
            
        self.card_counter = self.create_card(self.root, "Contador de Peças")
        self.card_counter.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.labels_contadores = {}
        for cor in self.contadores:
            row = tk.Frame(self.card_counter, bg="#1E1E2F")
            row.pack(fill="x", padx=15, pady=2)
            tk.Label(row, text=f"{cor}:", fg="white", bg="#1E1E2F", font=("Segoe UI", 11)).pack(side="left")
            lbl = tk.Label(row, text="0", fg="white", bg="#1E1E2F", font=("Segoe UI", 11))
            lbl.pack(side="right")
            self.labels_contadores[cor] = lbl
                
        self.card_calibracao = self.create_card(self.root, "Calibração")
        self.card_calibracao.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.btn_calibrar = ttk.Button(self.card_calibracao, text="  Abrir Calibração", image=self.calibrate_icon, compound="left", command=self.abrir_calibracao, style="Rounded.TButton", cursor="hand2")
        self.btn_calibrar.pack(pady=20)
        
        self.card_slider = self.create_card(self.root, "Ajuste de Thresholds")
        self.card_slider.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        self.sliders = {}
        for nome, val in zip(["Preto", "Cromado", "Transparente"], [40, 20, 30]):
            row = tk.Frame(self.card_slider, bg="#1E1E2F")
            row.pack(fill="x", padx=10, pady=5)
            tk.Label(row, text=f"{nome}:", fg="white", bg="#1E1E2F", font=("Segoe UI", 11)).pack(side="left")
            slider = ttk.Scale(row, from_=0, to=255, orient="horizontal", style="Dark.Horizontal.TScale", command=self.atualizar_valores_threshold)
            slider.configure(cursor="hand2")
            slider.set(val)
            slider.pack(side="left", fill="x", expand=True, padx=10)
            lbl = tk.Label(row, text=str(val), fg="white", bg="#1E1E2F", font=("Segoe UI", 11, "bold"))
            lbl.pack(side="right")
            self.sliders[nome] = (slider, lbl)
        
        self.slider_thresh_preto = self.sliders["Preto"][0]
        self.label_valor_preto = self.sliders["Preto"][1]
        self.slider_thresh_cromado = self.sliders["Cromado"][0]
        self.label_valor_cromado = self.sliders["Cromado"][1]
        self.slider_thresh_transparente = self.sliders["Transparente"][0]
        self.label_valor_transparente = self.sliders["Transparente"][1]


    def atualizar_registradores_modbus(self):
        if self.servidor_modbus:
            dados = {
                "Vermelho": self.contadores["Vermelho"],
                "Preto": self.contadores["Preto"],
                "Cromado": self.contadores["Cromado"],
                "Transparente": self.contadores["Transparente"],
            }
        self.servidor_modbus.comunicaModbusTCP(dados)
    
    def loop_atualizacao_modbus(self):
        while self.atualizacao_continua:
            if self.selected_protocol.get() == "Modbus/TCP":
                self.atualizar_registradores_modbus()
            time.sleep(0.02)
    
    def selecionaProtocolo(self):
        selected = self.selected_protocol.get()
        
        
        if not selected:
            messagebox.showwarning("Atenção", "Você deve selecionar um protocolo!")
            return 
            
        self.parar_atualizacao()
        
        try:
            self.modbusTCP.desativaServidorModbusTCP()
        
        except Exception as e:
            messagebox.showerror("Erro ao desligar Modbus:", e)
            
        try:
            self.mqtt.desativaMQTT()
        
        except Exception as e:
            messagebox.showerror("Erro ao desligar MQTT:", e)
            
        try:
            self.servidor_s7.desativaServidorS7()
        
        except Exception as e:
            messagebox.showerror("Erro ao desligar S7:", e)
            
        time.sleep(0.5)
        
        if selected == "Modbus/TCP":
            self.modbusTCP.ativaServidorModbus()
            self.servidor_s7.ativaServidorS7()
            self.mqtt.ativaMQTT()
            if not self.atualizacao_continua:
                self.atualizacao_continua = True
                self.thread_atualizacao = threading.Thread(target=self.loop_atualizacao_modbus, daemon=True)
                self.thread_atualizacao.start()
                
        elif selected == "S7":
            self.servidor_s7.ativaServidorS7()
            self.mqtt.ativaMQTT()
            self.modbusTCP.ativaServidorModbus()
            
        elif selected == "MQTT":
            self.mqtt.ativaMQTT()
            self.servidor_s7.ativaServidorS7()
            self.modbusTCP.ativaServidorModbus()
            
        for cor, valor in self.estado_atual_contagem.items():
            self.contadores[cor] = valor
            self.labels_contadores[cor].config(text=f"{valor}")
            
        self.dados_cores_atualizados = dict(self.estado_atual_contagem)
    
    def parar_atualizacao(self):
        self.atualizacao_continua = False
        if self.thread_atualizacao and self.thread_atualizacao.is_alive():
            self.thread_atualizacao.join(timeout=1)
            self.thread_atualizacao = None
    

    def enviar_dados_para_protocolo(self):
        data = {
            "Vermelho": self.contadores["Vermelho"],
            "Preto": self.contadores["Preto"],
            "Cromado": self.contadores["Cromado"],
            "Transparente": self.contadores["Transparente"],
        }
        
        protocolo = self.selected_protocol.get()
        
        if protocolo == "Modbus/TCP":
            self.modbusTCP.comunicaModbusTCP(data)
            self.mqtt.comunicaMQTT(data)
            self.servidor_s7.comunicaS7(data)
            
        elif protocolo == "S7":
            self.servidor_s7.comunicaS7(data)
            self.mqtt.comunicaMQTT(data)
            self.modbusTCP.comunicaModbusTCP(data)
        elif protocolo == "MQTT":
            self.mqtt.comunicaMQTT(data)
            self.servidor_s7.comunicaS7(data)
            self.modbusTCP.comunicaModbusTCP(data)
            
    def atualizar_valores_threshold(self, *_):
        if not hasattr(self, 'slider_thresh_preto'):
            return
                    
        self.threshold_preto = int(self.slider_thresh_preto.get())
        self.threshold_cromado = int(self.slider_thresh_cromado.get())
        self.threshold_transparente = int(self.slider_thresh_transparente.get())
        
        self.sliders["Preto"][1].config(text=str(self.threshold_preto))
        self.sliders["Cromado"][1].config(text=str(self.threshold_cromado))
        self.sliders["Transparente"][1].config(text=str(self.threshold_transparente))
                
        self.processo_imagem.atualizar_thresholds(
            self.threshold_preto,
            self.threshold_cromado,
            self.threshold_transparente
        )
    
    def iniciar(self):
        self.root.mainloop()

    
if __name__ == "__main__":
    app = Interface()
    app.iniciar()


