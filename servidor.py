import socket
import threading

class ImplementacaoServidor:
    def __init__(self, host, port, protocolo, confirmacaoCumulativa, tamanhoJanela):
        self.host = host
        self.port = port
        self.protocolo = protocolo
        self.confirmacaoCumulativa = confirmacaoCumulativa
        self.tamanhoJanela = tamanhoJanela
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.sequenciaEsperada = 1
        self.mensagensRecebidas = {}
        self.pacotesSemOrdem = {}
        self.janelaDeRecepcao = list(range(1, self.tamanhoJanela + 1))
        self.tamanhoBuffer = 1024

    def envioNak(self, conn, sequenciaDeNum):
        nak_data = f"NAK:{sequenciaDeNum}"
        checksum = self.calcular_checksum(nak_data)
        nak = f"{nak_data}:{checksum}\n"
        conn.sendall(nak.encode())
        print(f"Enviado: {nak.strip()}")

    def processamentoDePacotes(self, conn, sequenciaDeNum, conteudo, recebimentoChecksum):
        chacksumCalculado = self.calcular_checksum(conteudo)

        if len(conteudo) > self.tamanhoBuffer:
            print(f"Mensagem excede tamanho permitido ({self.tamanhoBuffer} bytes).")
            self.envioNak(conn, sequenciaDeNum)
            return

        if recebimentoChecksum != chacksumCalculado:
            print(f"Erro de checksum no pacote {sequenciaDeNum}: {conteudo}")
            if sequenciaDeNum not in self.mensagensRecebidas:
                self.envioNak(conn, sequenciaDeNum)
        elif sequenciaDeNum == self.sequenciaEsperada:
            print(f"Pacote {sequenciaDeNum} confirmado: {conteudo}")
            self.mensagensRecebidas[sequenciaDeNum] = conteudo
            self.enviar_ack(conn, sequenciaDeNum)
            self.atualizar_janela()

            while self.sequenciaEsperada in self.pacotesSemOrdem:
                conteudo_fora = self.pacotesSemOrdem.pop(self.sequenciaEsperada)
                print(f"Processando pacote fora de ordem: {self.sequenciaEsperada} - {conteudo_fora}")
                self.mensagensRecebidas[self.sequenciaEsperada] = conteudo_fora
                self.enviar_ack(conn, self.sequenciaEsperada)
                self.atualizar_janela()
        elif sequenciaDeNum in self.janelaDeRecepcao:
            print(f"Pacote {sequenciaDeNum} fora de ordem: {conteudo}. Dentro da janela: {self.janelaDeRecepcao}")
            self.pacotesSemOrdem[sequenciaDeNum] = conteudo
            self.envioNak(conn, self.sequenciaEsperada)
        else:
            if sequenciaDeNum < self.sequenciaEsperada:
                print(f"Pacote {sequenciaDeNum} já recebido anteriormente: {conteudo}")
                self.enviar_ack(conn, sequenciaDeNum)
            else:
                print(f"Pacote {sequenciaDeNum} fora da janela de recepção: {conteudo}. Esperado: {self.janelaDeRecepcao}")
                self.envioNak(conn, sequenciaDeNum)

    def calcular_checksum(self, mensagem):
        return sum(ord(c) for c in mensagem) & 0xFFFF

    def atualizar_janela(self):
        while self.sequenciaEsperada in self.mensagensRecebidas:
            self.sequenciaEsperada += 1
        self.janelaDeRecepcao = list(range(self.sequenciaEsperada, self.sequenciaEsperada + self.tamanhoJanela))
        print(f"Janela de recepção atualizada: {self.janelaDeRecepcao}")

    def enviar_ack(self, conn, sequenciaDeNum):
        ack_data = f"ACK:{sequenciaDeNum}"
        checksum = self.calcular_checksum(ack_data)
        ack = f"{ack_data}:{checksum}\n"
        conn.sendall(ack.encode())
        print(f"Enviado: {ack.strip()}")

    def extrair_handshake(self, mensagemDeHandshake):
        try:
            partes = mensagemDeHandshake.split(":")
            protocolo = partes[2]
            janela = partes[4]
            return protocolo.upper(), int(janela)
        except IndexError:
            print("Erro ao processar o handshake.")
            return None, None

    def receber_dados(self, conn):
        buffer = ""

        try:
            mensagemDeHandshake = conn.recv(1024).decode().strip()
            if mensagemDeHandshake.startswith("HANDSHAKE:"):
                print(f"Handshake recebido: {mensagemDeHandshake}")
                protocolo, janela = self.extrair_handshake(mensagemDeHandshake)

                if protocolo == self.protocolo and janela == self.tamanhoJanela:
                    ackDoHandshake = f"ACK_HANDSHAKE:PROTOCOL:{self.protocolo}:WINDOW:{self.tamanhoJanela}\n"
                    conn.sendall(ackDoHandshake.encode())
                    print(f"Handshake confirmado: {ackDoHandshake.strip()}")
                else:
                    print("Erro no handshake. Finalizando a conexão.")
                    conn.close()
                    return
            else:
                print("Mensagem inválida do handshake. Encerrando conexão.")
                conn.close()
                return
        except Exception as e:
            print(f"Erro durante o handshake: {e}")
            conn.close()
            return

        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    print("Cliente desconectado.")
                    break

                buffer += data
                while "\n" in buffer:
                    linha, buffer = buffer.split("\n", 1)

                    if ";" in linha:
                        pacotes = linha.split(";")
                        for pacote in pacotes:
                            self.processarPacotes(conn, pacote.strip())
                    else:
                        self.processarPacotes(conn, linha.strip())

            except ConnectionResetError:
                print("Cliente encerrou a conexão inesperadamente.")
                break
            except Exception as e:
                print(f"Erro na comunicação: {e}")
                break
        conn.close()
        print("Conexão encerrada pelo cliente.")

    def processarPacotes(self, conn, linha):
        partes = linha.split(":")
        if len(partes) >= 4:
            comando, sequenciaDeNumStr, conteudo, recebimentoChecksumStr = partes
            sequenciaDeNum = int(sequenciaDeNumStr)
            recebimentoChecksum = int(recebimentoChecksumStr)

            print(f"Recebido {comando}:{sequenciaDeNum}:{conteudo} (Checksum recebido: {recebimentoChecksum})")

            if comando == "SEND":
                self.processamentoDePacotes(conn, sequenciaDeNum, conteudo, recebimentoChecksum)
            elif comando == "ERR":
                print(f"Pacote {sequenciaDeNum} corrompido recebido (ERR): {conteudo}")
                self.envioNak(conn, sequenciaDeNum)
        else:
            print(f"Mensagem recebida em formato desconhecido: {linha.strip()}")

    def iniciar(self):
        print("Aguardando conexão...")
        while True:
            conn, addr = self.socket.accept()
            print(f"Conexão com {addr} estabelecida.")
            client_thread = threading.Thread(target=self.receber_dados, args=(conn,))
            client_thread.daemon = True
            client_thread.start()

def menuImplementacaoServidor():
    host = input("Digite o endereço do servidor (127.0.0.1): ") or "127.0.0.1"
    port = int(input("Digite a porta do servidor: ") or 123)
    protocolo = input("Escolha o protocolo (SR ou GBN): ").upper()
    confirmacaoCumulativa = input("Deseja confirmar pacotes cumulativamente? (s/n): ").lower() == "s"
    tamanhoJanela = int(input("Digite o tamanho da janela de recepção: "))
    servidor = ImplementacaoServidor(host, port, protocolo, confirmacaoCumulativa, tamanhoJanela)
    servidor.iniciar()

if __name__ == "__main__":
    menuImplementacaoServidor()
