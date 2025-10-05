import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from telaPrincipal import Ui_telaPrincipal

API_KEY = "b22fe5277cb5c8ba384f351b3b36605f"  

class AlertaTempestade(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(AlertaTempestade, self).__init__(*args, **kwargs)
        self.ui = Ui_telaPrincipal()
        self.ui.setupUi(self)
        self.ui.BTN_VERIFICARCLIMA.clicked.connect(self.verificar_clima)
        
        # Fonte monoespaçada para alinhamento perfeito
        font = QFont("Courier New", 9)
        self.ui.LABEL_RESULTADO.setFont(font)

        self.timer = QTimer()
        self.timer.timeout.connect(self.verificar_clima)
        self.timer.start(600000)

    def criar_grafico_textual(self, dados, cidade, largura_maxima=18):
        # Extrair os dados
        descricao = dados["weather"][0]["description"]
        vento = dados["wind"]["speed"]
        temperatura = dados["main"]["temp"]
        umidade = dados["main"]["humidity"]
        probabilidade_chuva = dados.get("rain", {}).get("1h", 0) * 100
        
        # Determinar status
        status = "Normal!"
        if "chuva" in descricao.lower() or vento > 15 or umidade > 80 or probabilidade_chuva > 50:
            status = "⚠️ ALERTA!"
        else:
            status = "✅ EMINENTE!"
        
        # Classificar umidade
        umidade_categoria = "Normal!" if umidade < 80 else "Alta"
        
        # Criar barras de progresso (largura reduzida para 18)
        barras_temp = min(int((temperatura / 40) * largura_maxima), largura_maxima)
        grafico_temp = "🌡️ " + "█" * barras_temp + "░" * (largura_maxima - barras_temp) + f"{temperatura}°C"
        
        barras_umid = min(int((umidade / 100) * largura_maxima), largura_maxima)
        grafico_umidade = "💧 " + "█" * barras_umid + "░" * (largura_maxima - barras_umid) + f"{umidade}%({umidade_categoria})"
        
        barras_vento = min(int((vento / 20) * largura_maxima), largura_maxima)
        grafico_vento = "💨 " + "█" * barras_vento + "░" * (largura_maxima - barras_vento) + f"{vento}m/s"
        
        barras_chuva = min(int((probabilidade_chuva / 100) * largura_maxima), largura_maxima)
        grafico_chuva = "🌧️ " + "█" * barras_chuva + "░ " * (largura_maxima - barras_chuva) + f"{probabilidade_chuva:.0f}%"
        
        # Barra de status
        barra_status = "█" * largura_maxima if "ALERTA!" in status else "░ " * largura_maxima
        grafico_status = "🚨 " + barra_status + f"{status}"
        
        # Formatar descrição
        descricao_formatada = descricao.capitalize()
        if len(descricao_formatada) > 28:
            descricao_formatada = descricao_formatada[:25] + "..."
        
        # Montar resultado com alinhamento PERFEITO
        resultado = f"""
╔═══════════════════════════════════════════════╗
║       PREVISÃO DO TEMPO - {cidade.upper():19} ║
╠═══════════════════════════════════════════════╣
║ {grafico_status:44}║
║ {grafico_temp:44} ║
║ {grafico_umidade:44}║
║ {grafico_vento:44} ║
║ {grafico_chuva:45} ║
║ ☁️Condição: {descricao_formatada:33}║
╚═══════════════════════════════════════════════╝
"""
        return resultado

    def verificar_clima(self):
        cidade = self.ui.TXT_INPUTCIDADE.text().strip()
        if not cidade:
            QMessageBox.warning(self, "Erro", "Por favor, digite uma cidade.")
            return

        url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br&units=metric"
        
        try:
            resposta = requests.get(url, timeout=10)
            dados = resposta.json()

            if dados.get("cod") != 200:
                QMessageBox.warning(self, "Erro", f"Não foi possível obter dados para {cidade}. Verifique se o nome está correto.")
                return

            alerta = self.criar_grafico_textual(dados, cidade)
            self.ui.LABEL_RESULTADO.setText(alerta)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Não foi possível conectar ao serviço: {e}")
        except KeyError as e:
            QMessageBox.critical(self, "Erro de Dados", f"Dados recebidos estão incompletos: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlertaTempestade()
    window.show()
    sys.exit(app.exec_())