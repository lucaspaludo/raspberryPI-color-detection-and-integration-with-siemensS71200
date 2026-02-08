from pyModbusTCP.server import ModbusServer

class ModbusTCP:
    def __init__(self):
        self.server = ModbusServer(host='172.16.87.127', port=502, no_block=True)
        
    def desativaServidorModbusTCP(self):
        print("Desligando servidor Modbus...")
        self.server.stop()
        

    def ativaServidorModbus(self):
        print("Iniciando Servidor Modbus...")
        
        self.server.start()
        
        print("Servidor inicado com sucesso!")
        # Desligar S7 e MQTT

    def comunicaModbusTCP(self, data):
        try:
            self.server.data_bank.set_holding_registers(0, [data["Vermelho"]])
            self.server.data_bank.set_holding_registers(1, [data["Preto"]])
            self.server.data_bank.set_holding_registers(2, [data["Cromado"]])
            self.server.data_bank.set_holding_registers(3, [data["Transparente"]])
            print("Registradores atualizados:", data)
            
        except Exception as e:
            print("Erro ao escrever no Modbus:", e)
            
            
        
