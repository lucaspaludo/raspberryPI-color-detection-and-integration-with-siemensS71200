# Sistema de Identificação Visual e Contagem de Peças (OpenCV + Modbus/TCP + S7 + MQTT)

O projeto apresenta o desenvolvimento de um sistema de visão computacional e
contagem de peças em uma planta de automação industrial utilizando Raspberry Pi 3, com
comunicação integrada entre os protocolos MODBUS/TCP, S7 e MQTT e um CLP Siemens
S7-1200. O sistema foi projetado para reconhecer cores distintas de peças (vermelho, preto,
prata e transparente) e transmitir as informações por meio de diferentes protocolos de rede. A
aplicação inclui interface gráfica para escolha do protocolo e visualização em tempo real.

> Projeto desenvolvido no contexto de automação industrial, com interface gráfica em **Tkinter** para seleção de protocolo, calibração e monitoramento em tempo real.

---

## ✨ Visão geral

- 🎥 Captura contínua via câmera USB (Raspberry Pi)
- 🎯 Detecção por **HSV**, **ROI**, limiarização e operações morfológicas
- 🧠 Estratégias específicas para **preto**, **cromado** e **transparente** com **subtração de fundo**
- 🧩 Arquitetura documentada com **Modelo C4**
- 🌐 Integração industrial:
  - **Modbus/TCP** (porta 502)
  - **S7** (Snap7) com escrita em **DB** via offset
  - **MQTT** (publish/subscribe) via broker

📄 Documentação completa:
- [`docs/Relatorio_Final.pdf`](docs/Relatorio_Final.pdf)
- [`docs/Apresentacao.pdf`](docs/Apresentacao.pdf)

---

## 🧱 Arquitetura (Modelo C4)

O sistema é dividido em três grandes domínios:

- **Vision (OpenCV)**: detecção de cor e contagem no ROI  
- **UI (Tkinter)**: seleção do protocolo, calibração e painel ao vivo  
- **Comm**: comunicação via Modbus/TCP, S7 e MQTT

> No relatório, a camada de código é composta por classes como **CameraManager**, **ProcessaImagem**, **Calibracao**, **Interface** e módulos de comunicação (**ModbusTCP**, **S7Client**, **Mqtt**).

---

## 🔁 Fluxo do sistema

1. Usuário seleciona o protocolo na interface  
2. Câmera verifica presença de peça na esteira  
3. Raspberry identifica a peça, classifica a cor e incrementa contadores  
4. Dados são disponibilizados para o CLP/consumidores via protocolo selecionado  
5. CLP acessa a informação (contagem/cor) para lógica de automação

---

## 🎨 Detecção de cores (resumo)

### Vermelho
- Máscara em HSV (faixas de vermelho)
- Dilatação + contornos + filtro por área e ROI

### Preto
- Desafio: esteira também é preta  
- Solução: **subtração de fundo** (absdiff) + limiarização + máscara HSV de preto

### Cromado
- Desafio: alto brilho/reflexividade  
- Solução: subtração de fundo + máscara HSV (baixo S e alto V) + limiarização mais sensível

### Transparente
- Desafio: não tem cor definida, fundo “aparece” através  
- Solução: subtração de fundo com threshold sensível + morfologia para contorno consistente

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

---

## 🚀 Como executar

### 1) Requisitos
- Raspberry Pi OS
- Python 3.9+
- Câmera USB
- (Opcional) CLP Siemens S7-1200 e/ou Broker MQTT

### 2) Instalação
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPO.git
cd SEU_REPO

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
