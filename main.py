from Interface.interface import Interface
from ModbusTCP.modbusTCP import ModbusTCP
from MQTT.mqtt import MQTT


if __name__ == "__main__":
    modbus = ModbusTCP()
    mqtt = MQTT()
    app = Interface(modbusTCP=modbus, mqtt=mqtt)
    app.iniciar()
