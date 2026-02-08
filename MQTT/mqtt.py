import paho.mqtt.client as mqtt
import snap7
from snap7.util import set_int
import snap7
from snap7.util import set_int, set_bool

class MQTT:
    def __init__(self, ip='172.16.87.61', rack=0, slot=1, db_number=3):
        
        self.client = mqtt.Client()
        self.client_s7 = snap7.client.Client()
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.db_number = db_number
        self.db = None
        self.db_size = 16 #ajustar valor real
                
        self.broker = "191.52.39.88"
        self.port = 1883
        self.topic = "projeto/cores"


    def desativaMQTT(self):
        try:
            self.client.disconnect()
            print("MQTT desconectado")
            self.client_s7.disconnect()
            print("Desconectado do CLP com sucesso")
            
        except Exception as e:
            print("Erro ao desconectar do CLP: ", e)

    def ativaMQTT(self):
        print("Iniciando MQTT")
        try:
            print("MQTT conectado")
            #conecta MQTT
            self.client.connect(self.broker, self.port, 60)
                       
            if self.client_s7.get_connected():
                print("Ja esta conectadp ao CLP")
                return
                
            self.client_s7.connect(self.ip, self.rack, self.slot)
            
            if self.client_s7.get_connected():
                print("Conectado ao CLP com sucesso")
                self.db = self.client_s7.db_read(self.db_number, 0, 9)
            else:
                print("Falha na conexao com CLP")

        except Exception as e:
            print("Erro ao conectar MQTT:", e)
            print("Erro ao conectar com CLP: ", e)

    def comunicaMQTT(self, data):
        try:
            payload = str(data)
            self.client.publish(self.topic, payload)
            print("MQTT publicou:", payload)
            
            self.db = self.client_s7.db_read(self.db_number, 0, 9)
            set_int(self.db, 0, data["Vermelho"])
            set_int(self.db, 2, data["Preto"])
            set_int(self.db, 4, data["Cromado"])
            set_int(self.db, 6, data["Transparente"])
            set_bool(self.db, 8, 0, True)
            self.client_s7.db_write(self.db_number, 0, self.db)
            set_bool(self.db, 8, 0, True)
            print("Dados enviados ao CLP")
        except Exception as e:
            print("Erro ao publicar MQTT", e)
