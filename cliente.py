import socket
import threading
import time
import random
import os

class ImplementacaoCliente:
    def __init__(self, host, port, probabilidadeErro, janela, numeroMensagens, protocolo):
        self.host = host
        self.port = port
        self.probabilidadeErro = probabilidadeErro
        self.janela = janela
        self.numeroMensagens = numeroMensagens
        self.protocolo = protocolo.upper()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.acksRecebidos = set()
        self.dadosEnviados = {}
        self.timeout = 2
        self.threadTimer = {}
        self.dadosDeBuffer = []
        self.tamanhoBuffer = 1024

    def recebimentoDeRespostas(self):
        buffer = ""
        while len(self.acksRecebidos) < self.numeroMensagens:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    linha, buffer = buffer.split("\n", 1)
                    partes = linha.split(":")
                    if len(partes) < 3:
                        continue
                    tipo, sequenciaStr, strChecksum = partes
                    sequenciaDeNumeros = int(sequenciaStr)
                    checksum = int(strChecksum)

                    esperado = f"{tipo}:{sequenciaDeNumeros}"
                    if self.calculoChecksum(esperado) == checksum:
                        if tipo == "ACK":
                            print(f"Recebido ACK para pacote {sequenciaDeNumeros}")
                            self.acksRecebidos.add(sequenciaDeNumeros)
                            self.cancelar_timer(sequenciaDeNumeros)
                        elif tipo == "NAK":
                            print(f"NAK recebido para o pacote {sequenciaDeNumeros}, retransmitindo...")
                            if sequenciaDeNumeros not in self.acksRecebidos:
                                self.enviar_pacote(sequenciaDeNumeros, self.dadosDeBuffer[sequenciaDeNumeros - 1])
                                self.iniciar_timer(sequenciaDeNumeros)
                    else:
                        print(f"Resposta corrompida: {linha}")
            except Exception as e:
                print(f"Erro ao receber resposta: {e}")

    def iniciar_envio(self, modoDeEnvio="unico"):
        self.carregar_dados()
        threading.Thread(target=self.recebimentoDeRespostas, daemon=True).start()

        if modoDeEnvio == "unico":
            for sequenciaDeNumeros in range(1, self.numeroMensagens + 1):
                if sequenciaDeNumeros not in self.acksRecebidos:
                    self.enviar_pacote(sequenciaDeNumeros, self.dadosDeBuffer[sequenciaDeNumeros - 1])
                    self.iniciar_timer(sequenciaDeNumeros)
        elif modoDeEnvio == "rajada":
            pacotes_para_enviar = []
            for sequenciaDeNumeros in range(1, self.numeroMensagens + 1):
                if sequenciaDeNumeros not in self.acksRecebidos:
                    mensagem = self.dadosDeBuffer[sequenciaDeNumeros - 1]
                    checksum = self.calculoChecksum(mensagem)
                    pacote = f"SEND:{sequenciaDeNumeros}:{mensagem}:{checksum}"
                    pacotes_para_enviar.append(pacote)

            modoRajada = ";".join(pacotes_para_enviar) + "\n"
            try:
                self.socket.sendall(modoRajada.encode())
                print(f"Enviado em rajada: {modoRajada.strip()}")
            except Exception as e:
                print(f"Erro ao enviar pacotes em rajada: {e}")

        while len(self.acksRecebidos) < self.numeroMensagens:
            time.sleep(1)

        print("Todos os pacotes foram confirmados. Encerrando...")

    def fechar_conexao(self):
        self.socket.close()
        print("Conexão fechada.")

    def handshake(self):
        mensagemHandshake = f"HANDSHAKE:PROTOCOL:{self.protocolo}:WINDOW:{self.janela}"
        self.socket.sendall(f"{mensagemHandshake}\n".encode())
        print(f"Handshake enviado: {mensagemHandshake}")
        ack_handshake = self.socket.recv(1024).decode().strip()

        if ack_handshake.startswith(f"ACK_HANDSHAKE:PROTOCOL:{self.protocolo}:WINDOW:{self.janela}"):
            print(f"Handshake confirmado pelo servidor: {ack_handshake}")
        else:
            print("Falha no handshake. Encerrando conexão.")
            self.socket.close()
            exit()

    def carregar_dados(self):
        path = os.path.join(os.path.dirname(__file__), "mensagens.txt")
        try:
            with open(path, "r") as arquivo:
                self.dadosDeBuffer = [
                    linha.strip()[:self.tamanhoBuffer]
                    for linha in arquivo.read().split(",")
                ]
                print(f"Mensagens carregadas (limitadas a {self.tamanhoBuffer} bytes cada).")
        except FileNotFoundError:
            print("Arquivo mensagens.txt não encontrado. Usando mensagens genéricas.")
            self.dadosDeBuffer = [
                f"Mensagem {i + 1}"[:self.tamanhoBuffer]
                for i in range(self.numeroMensagens)
            ]

    def calculoChecksum(self, mensagem):
        return sum(ord(c) for c in mensagem) & 0xFFFF

    def enviar_pacote(self, sequenciaDeNumeros, mensagem):
        checksum = self.calculoChecksum(mensagem)
        if random.random() < self.probabilidadeErro:
            mensagem = f"ERR:{sequenciaDeNumeros}:{mensagem[::-1]}:{checksum}"
            print(f"Simulando falha no pacote {sequenciaDeNumeros}")
        else:
            mensagem = f"SEND:{sequenciaDeNumeros}:{mensagem}:{checksum}"
        try:
            self.socket.sendall(f"{mensagem}\n".encode())
            self.dadosEnviados[sequenciaDeNumeros] = mensagem
            print(f"Enviado: {mensagem}")
        except Exception as e:
            print(f"Erro ao enviar pacote {sequenciaDeNumeros}: {e}")

    def iniciar_timer(self, sequenciaDeNumeros):
        def timer_expirado():
            if sequenciaDeNumeros not in self.acksRecebidos:
                print(f"Timeout para pacote {sequenciaDeNumeros}, retransmitindo...")
                self.enviar_pacote(sequenciaDeNumeros, self.dadosDeBuffer[sequenciaDeNumeros - 1])
                self.iniciar_timer(sequenciaDeNumeros)

        if sequenciaDeNumeros in self.threadTimer:
            self.threadTimer[sequenciaDeNumeros].cancel()

        timer = threading.Timer(self.timeout, timer_expirado)
        timer.start()
        self.threadTimer[sequenciaDeNumeros] = timer

    def cancelar_timer(self, sequenciaDeNumeros):
        if sequenciaDeNumeros in self.threadTimer:
            self.threadTimer[sequenciaDeNumeros].cancel()
            del self.threadTimer[sequenciaDeNumeros]

def menuDeImplementacaoCliente():
    host = input("Digite o endereço do servidor (127.0.0.1): ") or "127.0.0.1"
    port = int(input("Digite a porta do servidor: ") or 123)
    probabilidadeErro = float(input("Digite a probabilidade de erro: "))
    janela = int(input("Digite o tamanho inicial da janela: "))
    numeroMensagens = int(input("Digite o número de mensagens a enviar: "))
    protocolo = input("Escolha o protocolo (SR ou GBN): ").upper()
    modoDeEnvio = input("Escolha o modo de envio (unico/rajada): ").lower()

    cliente = ImplementacaoCliente(host, port, probabilidadeErro, janela, numeroMensagens, protocolo)
    cliente.handshake()
    if modoDeEnvio == "unico":
        cliente.iniciar_envio()
    elif modoDeEnvio == "rajada":
        cliente.iniciar_envio()
    cliente.fechar_conexao()

if __name__ == "__main__":
    menuDeImplementacaoCliente()
