# Aplicação Cliente-Servidor com Controle de Fluxo e Retransmissão
## Descrição
Este projeto é uma aplicação cliente-servidor em Python que implementa um protocolo de comunicação confiável na camada de aplicação, considerando um canal com perdas e erros simulados. Ele utiliza um sistema de janela deslizante para controle de fluxo e congestionamento, além de temporizadores para garantir a retransmissão de pacotes perdidos.

O servidor suporta dois modos de controle de retransmissão:

Go-Back-N
Selective Repeat (Repetição Seletiva)

## Funcionalidades
Transporte Confiável de Dados: Implementa confirmações de pacotes, números de sequência, retransmissão e simulação de perdas e erros.
Janela Deslizante: Gerencia o envio e recebimento de pacotes para controle de fluxo.
Temporizador de Retransmissão: Garante a retransmissão automática de pacotes não confirmados dentro do tempo limite.
Modos de Operação: Suporte aos modos Go-Back-N e Selective Repeat.
Simulação de Erros: Insere erros em pacotes e confirmações para simular falhas no canal de comunicação.

## Estrutura do Projeto:

projeto_cliente_servidor/
├── cliente/
│   ├── cliente.py
│   ├── protocoloCliente.py
│   ├── simulador_erros.py
│   └── utils.py
├── servidor/
│   ├── servidor.py
│   ├── protocoloServidor.py
│   ├── simulador_erros.py
│   └── utils.py
├── ambos/
│   ├── utils.py
│   ├── simuladorErros.py
└── README.md

## Requisitos
Python 3.8 ou superior
Bibliotecas padrão do Python

## Como Executar o Projeto

Passo 1: Clonar o Repositório
git clone https://github.com/username/repo.git
cd repo

Passo 2: Executar o Servidor
cd servidor
python3 servidor.py
O servidor estará agora aguardando conexões de clientes.

Passo 3: Executar o Cliente em outro terminal:

cd cliente
python3 cliente.py
O cliente tentará se conectar ao servidor e começará a enviar pacotes conforme configurado, exibindo um relatório de status ao final.

## Modos de Operação
Go-Back-N: O servidor aceita apenas pacotes na sequência exata e solicita retransmissão de pacotes fora de ordem.
Selective Repeat: O servidor aceita pacotes fora de ordem e confirma cada pacote individualmente.
Para alternar entre os modos, altere a variável modo_retransmissao no arquivo servidor.py.

## Detalhes Técnicos
Protocolo de Comunicação
Número de Sequência: Cada pacote inclui um número de sequência para controle de ordem.
ACK e NAK: O servidor responde com ACK para pacotes recebidos corretamente e NAK para pacotes fora de ordem (no modo Go-Back-N).
Janela Deslizante: O cliente envia múltiplos pacotes dentro de uma janela antes de esperar por ACKs.
Simulação de Perda e Erro: Funções que inserem falhas em pacotes e confirmações para simular um canal com falhas.
Exemplo de Execução

## Saída do Cliente:
Conectado ao servidor em 127.0.0.1:12346
Enviado: SEND:0:Pacote 0
Resposta: ACK:0
Pacote 1 simulado como perdido.
Enviado: SEND:2:Pacote 2
Resposta: ACK:2
Enviado: SEND:3:Pacote 3
Resposta: ACK:3
Retransmitindo pacote 1 devido ao timeout.
Relatório de Status:
Pacotes enviados: 4
Pacotes retransmitidos: 1

## Saída do Servidor
Servidor iniciado em 127.0.0.1:12346 no modo Selective Repeat
Conexão estabelecida com ('127.0.0.1', 61978)
Recebido: SEND:0:Pacote 0
Enviado: ACK:0
Recebido: SEND:2:Pacote 2
Enviado: ACK:2
Recebido: SEND:3:Pacote 3
Enviado: ACK:3
Recebido: SEND:1:Pacote 1
Simulando perda de ACK. Nenhuma confirmação enviada.

Licença
Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.
