import snap7
from snap7.util import set_int
from snap7.server import Server
import snap7
from snap7.util import set_int, set_bool
import threading

class S7Client:
	def __init__(self, ip='172.16.87.61', rack=0, slot=1, db_number=7):
		self.client = snap7.client.Client()
		self.ip = ip
		self.rack = rack
		self.slot = slot
		self.db_number = db_number
		self.db_size = 16 #ajustar valor real
		self.db = None
				
	def ativaServidorS7(self):
		try:
			if self.client.get_connected():
				print("Ja esta conectadp ao CLP")
				return
			
		#try:
			self.client.connect(self.ip, self.rack, self.slot)
			if self.client.get_connected():
				print("Conectado ao CLP com sucesso")
				self.db = self.client.db_read(self.db_number, 0, 9)
			else:
				print("Falha na conexao com CLP")
		except Exception as e:
			print("Erro ao conectar com CLP: ", e)
			
	def desativaServidorS7(self):
		try:
			self.client.disconnect()
			print("Desconectado do CLP com sucesso")
			
		except Exception as e:
			print("Erro ao desconectar do CLP: ", e)
			
			
	def comunicaS7(self, data):
		try:
			self.db = self.client.db_read(self.db_number, 0, 9)
				
			set_int(self.db, 0, data["Vermelho"])
			set_int(self.db, 2, data["Preto"])
			set_int(self.db, 4, data["Cromado"])
			set_int(self.db, 6, data["Transparente"])
			
			set_bool(self.db, 8, 0, True)
			self.client.db_write(self.db_number, 0, self.db)
			
			print("Dados enviados ao CLP via S7: ", data)
		except Exception as e:
			print("Erro ao escrever no CLP:", e)
			
