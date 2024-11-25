Aplicação Cliente-Servidor em Python
Descrição
Este projeto é uma aplicação cliente-servidor em Python que implementa um protocolo de comunicação confiável na camada de aplicação, simulando um canal com perdas e erros. Ele utiliza um sistema de janela deslizante para controle de fluxo e congestionamento, além de temporizadores para garantir a retransmissão de pacotes perdidos ou corrompidos.

O servidor suporta dois modos de controle de retransmissão:

Go-Back-N (GBN): O remetente envia vários pacotes sem esperar por confirmações individuais, mas deve retransmitir todos os pacotes a partir de um pacote perdido ou com erro.
Selective Repeat (SR): O remetente envia vários pacotes e apenas retransmite aqueles que não foram confirmados, permitindo confirmações individuais.
Funcionalidades
Transporte Confiável de Dados: Implementa confirmações de pacotes, números de sequência, retransmissão e simulação de perdas e erros.
Janela Deslizante: Gerencia o envio e recebimento de pacotes para controle de fluxo.
Temporizador de Retransmissão: Garante a retransmissão automática de pacotes não confirmados dentro do tempo limite.
Modos de Operação: Suporte aos modos Go-Back-N e Selective Repeat.
Simulação de Erros: Insere erros em pacotes para simular falhas no canal de comunicação.
Cálculo de Checksum: Verificação de integridade dos pacotes usando soma de verificação.

Requisitos
Python 3.8 ou superior
Bibliotecas padrão do Python

Como Executar o Projeto
Passo 1: Clonar o Repositório
git clone https://github.com/brandonhunt00/Cliente-Servidor.git
cd Cliente-Servidor
Passo 2: Executar o Servidor
Abra um terminal e navegue até o diretório do servidor:

cd servidor
python3 servidor.py
O servidor solicitará algumas configurações:

Endereço do servidor: Pressione Enter para usar 127.0.0.1.
Porta do servidor: Pressione Enter para usar a porta padrão 123.
Protocolo: Digite SR para Selective Repeat ou GBN para Go-Back-N.
Confirmação Cumulativa: Digite S para sim ou N para não.
Tamanho da Janela de Recepção: Insira um número inteiro para o tamanho da janela.
Passo 3: Executar o Cliente
Em outro terminal, navegue até o diretório do cliente:

cd cliente
python3 cliente.py
O cliente solicitará algumas configurações:

Endereço do servidor: Pressione Enter para usar 127.0.0.1.
Porta do servidor: Pressione Enter para usar a porta padrão 123.
Probabilidade de Erro: Insira um valor entre 0 e 1 (por exemplo, 0.1 para 10% de chance de erro).
Tamanho Inicial da Janela: Insira um número inteiro para o tamanho da janela.
Número de Mensagens a Enviar: Insira um número inteiro.
Protocolo: Digite SR para Selective Repeat ou GBN para Go-Back-N.
Modo de Envio: Digite unico para envio único ou rajada para envio em rajada.
Modos de Operação
Go-Back-N (GBN)
Funcionamento: O remetente pode enviar vários pacotes dentro da janela sem esperar por confirmações, mas se um pacote for perdido ou corrompido, todos os pacotes a partir desse ponto são retransmitidos.
Confirmação: Utiliza confirmações cumulativas; o ACK confirma todos os pacotes até aquele número de sequência.
Selective Repeat (SR)
Funcionamento: O remetente envia vários pacotes e apenas retransmite aqueles que não foram confirmados, permitindo confirmações individuais e aceitando pacotes fora de ordem.
Confirmação: Cada pacote é confirmado individualmente com um ACK.
Modo de Envio
Único (unico): O cliente envia pacotes individualmente, iniciando um temporizador para cada um.
Rajada (rajada): O cliente envia todos os pacotes de uma só vez, sem esperar por confirmações intermediárias.
Detalhes Técnicos
Protocolo de Comunicação
Handshake Inicial: Cliente e servidor trocam informações sobre o protocolo e o tamanho da janela antes de iniciar a comunicação.
Número de Sequência: Cada pacote inclui um número de sequência para controle de ordem.
Checksum: Verificação de integridade dos pacotes através da soma dos valores ASCII dos caracteres, limitada a 16 bits.
ACK e NAK: O servidor responde com ACK para pacotes recebidos corretamente e NAK para pacotes com erro ou fora de ordem (dependendo do protocolo).
Janela Deslizante: Gerencia o fluxo de dados, permitindo múltiplos pacotes em trânsito sem confirmação.
Simulação de Erros
Erros em Pacotes: O cliente simula erros invertendo o conteúdo do pacote com base na probabilidade definida.
Erros no Canal: A simulação ocorre apenas no cliente; não há simulação de perdas no canal de comunicação em si.
Cálculo de Checksum
Implementação: A soma de verificação é calculada somando os valores ASCII de todos os caracteres da mensagem e aplicando um AND com 0xFFFF para limitar a 16 bits.
Uso: Tanto o cliente quanto o servidor calculam o checksum para verificar a integridade dos pacotes.
Temporizadores e Retransmissão
Timeout: O cliente inicia um temporizador para cada pacote enviado. Se não receber um ACK antes do tempo limite, retransmite o pacote.
Gerenciamento de Temporizadores: Utiliza threads para controlar os temporizadores de cada pacote individualmente.
Exemplo de Execução
Saída do Cliente

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
Enviado: SEND:2:Mensagem 2:1027
Enviado: SEND:3:Mensagem 3:1029
Simulando falha no pacote 4
Enviado: ERR:4:4 megasseM:1031
Enviado: SEND:5:Mensagem 5:1033
Recebido ACK para pacote 1
Recebido ACK para pacote 2
Recebido ACK para pacote 3
Recebido NAK para pacote 4, retransmitindo...
Timeout para pacote 4, retransmitindo...
Enviado: SEND:4:Mensagem 4:1031
Recebido ACK para pacote 5
Recebido ACK para pacote 4
Todos os pacotes foram confirmados. Encerrando...
Conexão fechada.
Saída do Servidor

Digite o endereço do servidor (127.0.0.1): 
Digite a porta do servidor (123): 
Escolha o protocolo (SR para Selective Repeat ou GBN para Go-Back-N): SR
Deseja confirmar pacotes cumulativamente? (S/N): n
Digite o tamanho da janela de recepção: 5
Aguardando conexões...
Conexão com ('127.0.0.1', 54321) estabelecida.
Handshake recebido: HANDSHAKE:PROTOCOL:SR:WINDOW:5
Handshake confirmado: ACK_HANDSHAKE:PROTOCOL:SR:WINDOW:5
Recebido SEND:1:Mensagem 1 (Checksum recebido: 1025)
Pacote 1 confirmado: Mensagem 1
Enviado: ACK:1:66
Janela de recepção atualizada: [2, 3, 4, 5, 6]
Recebido SEND:2:Mensagem 2 (Checksum recebido: 1027)
Pacote 2 confirmado: Mensagem 2
Enviado: ACK:2:68
Janela de recepção atualizada: [3, 4, 5, 6, 7]
Recebido SEND:3:Mensagem 3 (Checksum recebido: 1029)
Pacote 3 confirmado: Mensagem 3
Enviado: ACK:3:70
Janela de recepção atualizada: [4, 5, 6, 7, 8]
Recebido ERR:4:4 megasseM (Checksum recebido: 1031)
Erro de checksum no pacote 4: 4 megasseM
Enviado: NAK:4:70
Recebido SEND:5:Mensagem 5 (Checksum recebido: 1033)
Pacote 5 confirmado: Mensagem 5
Enviado: ACK:5:72
Janela de recepção atualizada: [4, 6, 7, 8, 9]
Recebido SEND:4:Mensagem 4 (Checksum recebido: 1031)
Pacote 4 confirmado: Mensagem 4
Enviado: ACK:4:70
Janela de recepção atualizada: [6, 7, 8, 9, 10]
Conexão encerrada pelo cliente.
Observações Importantes
Arquivo de Mensagens: O cliente tenta carregar mensagens de um arquivo mensagens.txt. Se não encontrar o arquivo, gera mensagens genéricas.
Personalização: Você pode ajustar a probabilidade de erro, tamanho da janela, número de mensagens e outros parâmetros para simular diferentes condições de rede.
Extensibilidade: O código é modular e pode ser estendido para incluir novas funcionalidades, como suporte a UDP, criptografia ou autenticação.
Licença
Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.
