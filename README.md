# Sistema de Identificação Visual e Contagem de Peças (OpenCV + Modbus/TCP + S7 + MQTT)

O projeto apresenta o desenvolvimento de um sistema de visão computacional e
contagem de peças em uma planta de automação industrial utilizando Raspberry Pi 3, com
comunicação integrada entre os protocolos MODBUS/TCP, S7 e MQTT e um CLP Siemens
S7-1200. O sistema foi projetado para reconhecer cores distintas de peças (vermelho, preto,
prata e transparente) e transmitir as informações por meio de diferentes protocolos de rede. A
aplicação inclui interface gráfica para escolha do protocolo e visualização em tempo real.

> Projeto desenvolvido no contexto de automação industrial, com interface gráfica em **Tkinter** para seleção de protocolo, calibração e monitoramento em tempo real.

---

## Raspberry

Raspberry Pi se mostrou eficiente no gerenciamento de tarefas em tempo real
moderado, como a captura de imagens da câmera USB, o processamento do algoritmo de
identificação de cores e o envio dos dados identificados para múltiplos protocolos
simultaneamente.

<img width="1920" height="1080" alt="Projeto Integrador II" src="https://github.com/user-attachments/assets/3579f0b0-a0fa-43e9-8952-ef45e0f8e8b5" />

## Fluxo das informações
<img width="1920" height="1080" alt="Projeto Integrador II (1)" src="https://github.com/user-attachments/assets/0b38e4ee-e1d6-44c1-ac58-cb25cadf515b" />

---

## 🧱 Arquitetura (Modelo C4)

O sistema é dividido em três grandes domínios:

- **OpenCV**: detecção de cor e contagem no ROI  
- **Tkinter**: seleção do protocolo, calibração e painel ao vivo  
- **Comunicação**: comunicação via Modbus/TCP, S7 e MQTT

> A camada de código é composta por classes como **CameraManager**, **ProcessaImagem**, **Calibracao**, **Interface** e módulos de comunicação (**ModbusTCP**, **S7Client**, **Mqtt**).

---

## 🔁 Fluxo do sistema

1. Usuário seleciona o protocolo na interface  
2. Câmera verifica presença de peça na esteira  
3. Raspberry identifica a peça, classifica a cor e incrementa contadores  
4. Dados são disponibilizados para o CLP/consumidores via protocolo selecionado  
5. CLP acessa a informação (contagem/cor) para lógica de automação

---

## 🖥️ Interface (Tkinter)

A interface oferece:
- Seleção do protocolo (Modbus/TCP, S7 ou MQTT)
- Visualização ao vivo da câmera
- Contagem por cor
- Calibração com janela adicional (sobreposição de referência)
- Sliders para ajuste de thresholds (preto/cromado/transparente)

> Coloque aqui prints em `assets/images/` e referencie:
> - `assets/images/interface.jpg`
> - `assets/images/calibracao.jpg`

<img width="1920" height="1080" alt="Projeto Integrador II (2)" src="https://github.com/user-attachments/assets/92c36e5c-fc1a-45ba-9482-3b2ca50dacd0" />

---

## Requisitos
- Raspberry Pi OS
- Python 3.9+
- Câmera USB
- (Opcional) CLP Siemens S7-1200 e/ou Broker MQTT


## Funcionamento



