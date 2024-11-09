import socket
import time
import threading
import random

# Variável global para armazenar ACKs recebidos
ack_received = [False] * 100  # Controle de ACKs recebidos para até 100 pacotes (exemplo)

# Variáveis para o relatório de status
pacotes_enviados = 0
pacotes_retransmitidos = 0

class ProtocoloCliente:
    def __init__(self):
        self.mensagens = {
            "SEND": "SEND",
            "SEND_BURST": "SEND_BURST",
            "ERROR": "ERROR",
            "END": "END"
        }

    def mensagem_enviar(self, tipo, conteudo="", numero_sequencia=0):
        """
        Retorna uma mensagem formatada para envio ao servidor, incluindo número de sequência.
        """
        if tipo in self.mensagens:
            return f"{self.mensagens[tipo]}:{numero_sequencia}:{conteudo}"
        else:
            raise ValueError("Tipo de mensagem não suportado")

    def mensagem_receber(self, mensagem):
        """
        Processa a mensagem recebida do servidor e retorna o tipo, número de sequência e conteúdo.
        """
        partes = mensagem.split(":")
        tipo = partes[0]

        # Verifica se o número de sequência é um valor numérico
        try:
            numero_sequencia = int(partes[1])
        except ValueError:
            print(f"Aviso: número de sequência inválido na mensagem recebida: {partes[1]}")
            return tipo, None, partes[2] if len(partes) > 2 else ""

        conteudo = partes[2] if len(partes) > 2 else ""
        return tipo, numero_sequencia, conteudo

def introduzir_erro(mensagem, probabilidade_erro=0.1):
    """
    Introduz um erro no conteúdo da mensagem, preservando o tipo e o número de sequência.
    """
    partes = mensagem.split(":")
    if len(partes) >= 2:
        tipo = partes[0]
        numero_sequencia = partes[1]

        # Introduz erro no conteúdo, se houver
        if len(partes) > 2:
            conteudo = partes[2]
            conteudo_com_erro = ''.join(random.choice('!@#$%?') if random.random() < probabilidade_erro else c for c in conteudo)
            partes[2] = conteudo_com_erro
        mensagem_com_erro = ":".join(partes)
    else:
        mensagem_com_erro = mensagem  # Retorna a mensagem sem alterações se o formato estiver incorreto
    
    return mensagem_com_erro

def simular_perda():
    """
    Retorna True para simular uma perda de pacote com uma certa probabilidade.
    """
    probabilidade_perda = 0.1
    return random.random() < probabilidade_perda

def iniciar_cliente():
    global cliente_socket, pacotes_enviados, pacotes_retransmitidos

    host = '127.0.0.1'
    porta = 12346  # Porta atualizada para evitar conflitos

    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    protocolo = ProtocoloCliente()

    # Configurações da janela deslizante e temporizador
    window_size = 3
    timeout = 2
    base = 0
    next_seq_num = 0

    # Função para lidar com a recepção de ACKs
    def receber_ack():
        nonlocal base
        while True:
            try:
                resposta = cliente_socket.recv(1024).decode()
                tipo, seq, conteudo = protocolo.mensagem_receber(resposta)

                if seq is None:
                    print("Mensagem inválida recebida e ignorada.")
                    continue

                print(f"Resposta do servidor: Tipo={tipo}, Número de Sequência={seq}, Conteúdo={conteudo}")

                if tipo == "ACK" and seq >= base:
                    ack_received[seq] = True
                    while ack_received[base]:
                        base += 1

            except OSError:
                break

    try:
        cliente_socket.connect((host, porta))
        print(f"Conectado ao servidor em {host}:{porta}")

        threading.Thread(target=receber_ack, daemon=True).start()

        while True:
            while next_seq_num < base + window_size:
                mensagem = protocolo.mensagem_enviar("SEND", f"Pacote {next_seq_num}", next_seq_num)
                mensagem_com_erro = introduzir_erro(mensagem)

                if not simular_perda():
                    cliente_socket.send(mensagem_com_erro.encode())
                    pacotes_enviados += 1
                    print(f"Enviado para o servidor: {mensagem_com_erro}")
                else:
                    print(f"Pacote {next_seq_num} simulado como perdido.")

                threading.Timer(timeout, lambda seq=next_seq_num: retransmitir_pacote(seq)).start()

                next_seq_num += 1
                time.sleep(0.5)

    finally:
        cliente_socket.close()
        print("Conexão encerrada")
        print(f"Relatório de Status:")
        print(f"Pacotes enviados: {pacotes_enviados}")
        print(f"Pacotes retransmitidos: {pacotes_retransmitidos}")

def retransmitir_pacote(seq):
    global cliente_socket, pacotes_retransmitidos
    protocolo = ProtocoloCliente()
    if not ack_received[seq]:
        mensagem = protocolo.mensagem_enviar("SEND", f"Pacote {seq}", seq)
        cliente_socket.send(mensagem.encode())
        pacotes_retransmitidos += 1
        print(f"Retransmitindo pacote {seq} devido ao timeout.")

if __name__ == "__main__":
    iniciar_cliente()
