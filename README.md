# Protocolo de Transporte Confiável com Controle de Fluxo e Congestionamento

Este projeto implementa uma aplicação cliente-servidor capaz de fornecer um transporte confiável de dados na camada de aplicação, simulando um canal com perdas de dados e erros. Além disso, implementa controle de fluxo e controle de congestionamento. 

## Objetivo

Desenvolver uma aplicação de comunicação cliente-servidor que simule o envio confiável de pacotes, mesmo em um ambiente onde possam ocorrer perdas de dados e erros de integridade. A aplicação deve:
- Utilizar sockets para comunicação.
- Implementar um protocolo de aplicação customizado.
- Simular falhas de integridade e perdas de pacotes.
- Implementar controle de fluxo e controle de congestionamento.
- Fornecer uma checagem de integridade via checksum.

## Funcionalidades

### Cliente
- Envia pacotes individuais ou em lotes para o servidor.
- Simula erros de integridade em pacotes específicos.
- Controla a janela de congestionamento e o número de sequência.
- Suporta simulação de perda de pacotes e retransmissão.
  
### Servidor
- Recebe pacotes e verifica integridade utilizando checksum.
- Confirma pacotes recebidos com ACK ou sinaliza erros com NACK.
- Permite simular perda de confirmação (ACK) e inserir erros de integridade nos ACKs.
- Suporta negociação de protocolos (Go-Back-N ou Repetição Seletiva).

## Pré-requisitos

Para executar o projeto, você precisará de:
- Um ambiente Linux (pode usar [WSL](https://docs.microsoft.com/pt-br/windows/wsl/) no Windows).
- Compilador GCC para C.
- Privilégios de superusuário para executar sockets RAW.

## Configuração e Execução

### Compilação

1. Compile o código do cliente e servidor:
   ```bash
   gcc cliente.c -o cliente
   gcc servidor.c -o servidor
