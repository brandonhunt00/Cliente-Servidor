# Aplicação Cliente-Servidor

## Descrição

Este projeto é uma aplicação cliente-servidor em Python que implementa um protocolo de comunicação confiável na camada de aplicação, considerando um canal de comunicação com perdas e erros simulados. A aplicação utiliza um sistema de janela deslizante para controle de fluxo e congestionamento, além de temporizadores para garantir a retransmissão de pacotes perdidos.

O servidor suporta dois modos de controle de retransmissão: **Go-Back-N** e **Selective Repeat** (Repetição Seletiva), permitindo maior flexibilidade e adaptação a diferentes condições de rede.

## Funcionalidades

- **Transporte Confiável de Dados**: Implementa um protocolo com confirmação de pacotes, números de sequência, retransmissão de pacotes e simulação de perdas e erros.
- **Janela Deslizante**: Controle de fluxo utilizando uma janela deslizante para gerenciar o envio e recebimento de pacotes.
- **Temporizador de Retransmissão**: Retransmissão automática de pacotes não confirmados dentro do tempo limite especificado.
- **Modos de Operação**: Suporte aos modos Go-Back-N e Selective Repeat para controle de retransmissão.
- **Simulação de Erros**: Inserção de erros simulados nos pacotes para testar a robustez do protocolo.
- **Cálculo de Checksum**: Verificação da integridade dos pacotes utilizando soma de verificação.

## Requisitos

- Python 3.8 ou superior
- Bibliotecas padrão do Python

## Como Executar o Projeto

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/brandonhunt00/Cliente-Servidor.git
cd Cliente-Servidor
```
### Passo 2: Executar o Servidor
Abra um terminal e navegue até o diretório do servidor:

```bash
cd servidor
python3 servidor.py
```
O servidor solicitará as seguintes configurações:

Endereço do servidor: Pressione Enter para usar o valor padrão 127.0.0.1.
Porta do servidor: Pressione Enter para usar o valor padrão 123.
Protocolo: Digite SR para Selective Repeat ou GBN para Go-Back-N.
Confirmação Cumulativa: Digite S para ativar ou N para desativar.
Tamanho da Janela de Recepção: Insira o tamanho desejado para a janela.

### Passo 3: Executar o Cliente
Em outro terminal, navegue até o diretório do cliente:

```bash
cd cliente
python3 cliente.py
```
O cliente solicitará as seguintes configurações:

Endereço do servidor: Pressione Enter para usar o valor padrão 127.0.0.1.
Porta do servidor: Pressione Enter para usar o valor padrão 123.
Probabilidade de Erro: Insira um valor entre 0 e 1 (ex.: 0.1 para 10% de chance de erro).
Tamanho Inicial da Janela: Insira o tamanho desejado para a janela.
Número de Mensagens a Enviar: Insira o número total de mensagens.
Protocolo: Digite SR para Selective Repeat ou GBN para Go-Back-N.
Modo de Envio: Digite unico para envio sequencial ou rajada para envio em bloco.

### Modos de Operação
Go-Back-N (GBN)
Funcionamento: O remetente envia múltiplos pacotes sem esperar por confirmações. Se um pacote for perdido ou corrompido, todos os pacotes a partir do ponto de erro são retransmitidos.
Confirmação: Utiliza confirmações cumulativas para reduzir a sobrecarga de comunicação.
Selective Repeat (SR)
Funcionamento: Permite confirmações individuais e aceita pacotes fora de ordem. Apenas pacotes perdidos ou corrompidos são retransmitidos.
Confirmação: Cada pacote é confirmado individualmente, garantindo maior eficiência.

### Exemplo de Execução
## Saída do Cliente
Digite o endereço do servidor (127.0.0.1): 
Digite a porta do servidor (123): 
Digite a probabilidade de erro: 0.1
Digite o tamanho inicial da janela: 5
Digite o número de mensagens a enviar: 5
Escolha o protocolo (SR para Selective Repeat ou GBN para Go-Back-N): SR
Escolha o modo de envio (unico/rajada): unico
Handshake enviado: HANDSHAKE:PROTOCOL:SR:WINDOW:5
Handshake confirmado pelo servidor: ACK_HANDSHAKE:PROTOCOL:SR:WINDOW:5
Enviado: SEND:1:Mensagem 1:1025
Recebido ACK para pacote 1
...
Todos os pacotes foram confirmados. Encerrando...
Conexão fechada.

## Saída do Servidor
Aguardando conexões...
Conexão com ('127.0.0.1', 54321) estabelecida.
Handshake recebido: HANDSHAKE:PROTOCOL:SR:WINDOW:5
Handshake confirmado: ACK_HANDSHAKE:PROTOCOL:SR:WINDOW:5
Recebido SEND:1:Mensagem 1 (Checksum recebido: 1025)
Pacote 1 confirmado: Mensagem 1
Enviado: ACK:1:66
...
Conexão encerrada pelo cliente.

### Observações Importantes
Arquivo de Mensagens: O cliente tenta carregar mensagens de um arquivo mensagens.txt. Caso não encontre o arquivo, cria mensagens genéricas automaticamente.
Personalização: Ajuste os parâmetros como probabilidade de erro, tamanho da janela e número de mensagens para simular diferentes condições de rede.
Extensibilidade: O código pode ser facilmente adaptado para incluir novas funcionalidades, como suporte a UDP, autenticação ou criptografia.

### Licença
Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.
