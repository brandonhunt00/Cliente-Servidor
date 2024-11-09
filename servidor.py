import socket
import random

class ProtocoloServidor:
    def __init__(self):
        self.respostas = {
            "ACK": "ACK",
            "NAK": "NAK",
            "ACK_BATCH": "ACK_BATCH"
        }

    def resposta_enviar(self, tipo, numero_sequencia=0, conteudo=""):
        """
        Retorna uma resposta formatada para envio ao cliente, incluindo número de sequência.
        """
        if tipo in self.respostas:
            return f"{self.respostas[tipo]}:{numero_sequencia}:{conteudo}"
        else:
            raise ValueError("Tipo de resposta não suportado")

    def resposta_receber(self, resposta):
        """
        Processa a resposta recebida do cliente e retorna o tipo, número de sequência e conteúdo.
        """
        partes = resposta.split(":")
        tipo = partes[0]
        numero_sequencia = int(partes[1])
        conteudo = partes[2] if len(partes) > 2 else ""
        return tipo, numero_sequencia, conteudo

def introduzir_erro_ack(ack, probabilidade_erro=0.1):
    """
    Introduz um erro no conteúdo do ACK/NAK, preservando o tipo da mensagem e o número de sequência.
    """
    partes = ack.split(":")
    if len(partes) >= 2:
        # Preserva o tipo (ACK/NAK) e número de sequência
        tipo = partes[0]
        numero_sequencia = partes[1]

        # Introduz erro no conteúdo, se houver
        if len(partes) > 2:
            conteudo = partes[2]
            conteudo_com_erro = ''.join(random.choice('!@#$%?') if random.random() < probabilidade_erro else c for c in conteudo)
            partes[2] = conteudo_com_erro
        ack_com_erro = ":".join(partes)
    else:
        ack_com_erro = ack  # Retorna a mensagem sem alterações se o formato estiver incorreto
    
    return ack_com_erro

def simular_perda_ack():
    """
    Retorna True para simular a perda de um ACK.
    """
    probabilidade_perda_ack = 0.1
    return random.random() < probabilidade_perda_ack

def iniciar_servidor():
    host = '127.0.0.1'
    porta = 12346
    modo_retransmissao = "Selective Repeat"
    confirmacao_em_grupo = True  # Ativa a confirmação em grupo

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor_socket.bind((host, porta))
        servidor_socket.listen(5)
        print(f"Servidor iniciado em {host}:{porta} no modo {modo_retransmissao}")

        protocolo = ProtocoloServidor()
        numero_sequencia_esperado = 0
        janela_recebida = {}

        while True:
            cliente_socket, endereco = servidor_socket.accept()
            print(f"Conexão estabelecida com {endereco}")

            try:
                while True:
                    dados = cliente_socket.recv(1024).decode()
                    if not dados:
                        break
                    print(f"Recebido do cliente: {dados}")

                    tipo, seq, conteudo = protocolo.resposta_receber(dados)

                    if confirmacao_em_grupo:
                        if seq == numero_sequencia_esperado:
                            inicio = numero_sequencia_esperado
                            numero_sequencia_esperado += 1
                            while numero_sequencia_esperado in janela_recebida:
                                janela_recebida.pop(numero_sequencia_esperado)
                                numero_sequencia_esperado += 1
                            fim = numero_sequencia_esperado - 1
                            
                            # Envia ACK em grupo apenas se houver mais de um pacote no intervalo
                            if fim > inicio:
                                resposta = protocolo.resposta_enviar("ACK", f"{inicio}-{fim}")
                            else:
                                resposta = protocolo.resposta_enviar("ACK", f"{inicio}")
                        else:
                            resposta = protocolo.resposta_enviar("NAK", seq)
                            print("Número de sequência fora da janela, enviando NAK.")
                    else:
                        # Modo padrão de confirmação individual
                        if seq == numero_sequencia_esperado:
                            resposta = protocolo.resposta_enviar("ACK", seq)
                            numero_sequencia_esperado += 1
                        else:
                            resposta = protocolo.resposta_enviar("NAK", seq)
                            print("Número de sequência fora da janela, enviando NAK.")

                    if simular_perda_ack():
                        print("Simulando perda de ACK. Nenhuma confirmação enviada.")
                        continue

                    resposta_com_erro = introduzir_erro_ack(resposta)
                    cliente_socket.send(resposta_com_erro.encode())
                    print(f"Enviado para o cliente: {resposta_com_erro}")

            finally:
                cliente_socket.close()
                print(f"Conexão com {endereco} encerrada")

    finally:
        servidor_socket.close()
        print("Socket do servidor fechado")

if __name__ == "__main__":
    iniciar_servidor()
