#!/usr/bin/env python3
import subprocess
import time
import os
import signal

def run_test(test_name, server_args, client_args, expected_server_output, expected_client_output):
    print(f"\nExecutando teste: {test_name}")

    # Inicia o servidor
    server_cmd = ["sudo", "./servidor"] + server_args
    server_proc = subprocess.Popen(server_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Aguarda o servidor iniciar
    time.sleep(1)

    # Executa o cliente
    client_cmd = ["sudo", "./cliente"] + client_args
    client_proc = subprocess.Popen(client_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Aguarda o cliente terminar
    client_stdout, client_stderr = client_proc.communicate(timeout=10)

    # Aguarda um pouco e termina o servidor
    time.sleep(1)
    os.kill(server_proc.pid, signal.SIGINT)
    server_stdout, server_stderr = server_proc.communicate()

    # Verifica a saída do servidor
    server_output = server_stdout + server_stderr
    client_output = client_stdout + client_stderr

    server_pass = all(msg in server_output for msg in expected_server_output)
    client_pass = all(msg in client_output for msg in expected_client_output)

    if server_pass and client_pass:
        print(f"Teste {test_name}: PASSOU")
    else:
        print(f"Teste {test_name}: FALHOU")
        if not server_pass:
            print("Saída do servidor não contém as mensagens esperadas.")
            print("Saída do Servidor:")
            print(server_output)
        if not client_pass:
            print("Saída do cliente não contém as mensagens esperadas.")
            print("Saída do Cliente:")
            print(client_output)

# Compila o cliente e o servidor
subprocess.run(["gcc", "cliente.c", "-o", "cliente"])
subprocess.run(["gcc", "servidor.c", "-o", "servidor"])

# Lista de testes
tests = [
    {
        "test_name": "Teste de Comunicação Básica",
        "server_args": [],
        "client_args": [],
        "expected_server_output": ["Pacote recebido com sequência"],
        "expected_client_output": ["Pacote enviado com sequência"]
    },
    {
        "test_name": "Teste de Checagem de Integridade",
        "server_args": [],
        "client_args": ["-e", "1"],
        "expected_server_output": ["Erro de integridade detectado no pacote de sequência 0"],
        "expected_client_output": []
    },
    {
        "test_name": "Teste de Perda de ACK",
        "server_args": ["-l", "0"],
        "client_args": [],
        "expected_server_output": ["Não enviando ACK para sequência 0"],
        "expected_client_output": ["Timeout aguardando ACK para sequência 0"]
    },
    {
        "test_name": "Teste de NACK",
        "server_args": ["-n", "0"],
        "client_args": [],
        "expected_server_output": ["Enviando NACK para sequência 0"],
        "expected_client_output": ["NACK recebido para sequência 0"]
    },
    {
        "test_name": "Teste de Controle de Fluxo",
        "server_args": [],
        "client_args": ["-w", "5"],
        "expected_server_output": ["Pacote recebido com sequência"],
        "expected_client_output": ["Janela de congestionamento atualizada"]
    },
    {
        "test_name": "Teste de Negociação de Protocolo",
        "server_args": ["-p", "SR"],
        "client_args": ["-p", "SR"],
        "expected_server_output": ["Protocolo selecionado: SR"],
        "expected_client_output": ["Usando protocolo SR"]
    }
]

# Executa os testes
for test in tests:
    run_test(test["test_name"], test["server_args"], test["client_args"], test["expected_server_output"], test["expected_client_output"])

print("\nTestes finalizados.")
