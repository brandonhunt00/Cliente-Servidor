#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/ip.h>
#include <fcntl.h>
#include <getopt.h>  // Inclusão para processar argumentos de linha de comando

#define TAMANHO_BUFFER 4096
#define TAMANHO_DADOS 512
#define PORTA_SERVIDOR 8080

// Flags
#define FLAG_ACK 0x1
#define FLAG_NACK 0x2
#define FLAG_SYN 0x4
#define FLAG_FIN 0x8
#define FLAG_ERR 0x10  // Para simulação de erro

// Estrutura do nosso "UDP" simulado com novos campos
struct udp_simulado {
    uint16_t porta_origem;
    uint16_t porta_destino;
    uint16_t comprimento;
    uint16_t checksum;
    uint32_t seq_num;
    uint32_t ack_num;
    uint16_t flags;
    uint16_t window_size;
    char dados[TAMANHO_DADOS];
};

// Função para calcular o checksum
unsigned short checksum(void *b, int len) {
    unsigned short *buf = b;
    unsigned int sum = 0;
    for (; len > 1; len -= 2)
        sum += *buf++;
    if (len == 1)
        sum += *(unsigned char *)buf;
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    return (unsigned short)(~sum);
}

// Função para configurar o socket como não-bloqueante
void set_nonblocking(int sock) {
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);
}

int main(int argc, char *argv[]) {
    struct sockaddr_in cliente;
    int sock;
    char buffer[TAMANHO_BUFFER];
    struct iphdr *ip_header;
    struct udp_simulado *udp_payload;
    socklen_t tamanho_cliente;
    int bytes_recebidos;
    uint32_t expected_seq = 0;
    int ack_loss_packet = -1;
    int nack_packet = -1;
    int error_ack_packet = -1;
    uint16_t recv_window = 5;  // Janela de recepção
    char protocolo[10] = "GBN";  // Valor padrão

    // Variáveis para opções
    int opcao;

    // Processa os argumentos de linha de comando
    while ((opcao = getopt(argc, argv, "l:n:e:p:")) != -1) {
        switch (opcao) {
            case 'l':
                ack_loss_packet = atoi(optarg);
                break;
            case 'n':
                nack_packet = atoi(optarg);
                break;
            case 'e':
                error_ack_packet = atoi(optarg);
                break;
            case 'p':
                strcpy(protocolo, optarg);
                break;
            default:
                fprintf(stderr, "Uso: %s [-l ack_loss_packet] [-n nack_packet] [-e error_ack_packet] [-p protocolo]\n", argv[0]);
                exit(EXIT_FAILURE);
        }
    }

    printf("Configurações do Servidor:\n");
    printf("Não confirmar pacote de sequência: %d\n", ack_loss_packet);
    printf("Enviar NACK para pacote de sequência: %d\n", nack_packet);
    printf("Inserir erro de integridade no ACK para sequência: %d\n", error_ack_packet);
    printf("Protocolo: %s\n", protocolo);

    // Cria um socket RAW
    sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (sock < 0) {
        perror("Erro ao criar socket");
        return 1;
    }

    // Configura o socket como não-bloqueante
    set_nonblocking(sock);

    printf("Servidor esperando pacotes...\n");

    // Loop de recebimento
    while (1) {
        memset(buffer, 0, TAMANHO_BUFFER);
        tamanho_cliente = sizeof(cliente);

        // Recebe o pacote RAW
        bytes_recebidos = recvfrom(sock, buffer, TAMANHO_BUFFER, 0, (struct sockaddr *)&cliente, &tamanho_cliente);
        if (bytes_recebidos > 0) {
            // Analisa o cabeçalho IP
            ip_header = (struct iphdr *)buffer;
            udp_payload = (struct udp_simulado *)(buffer + ip_header->ihl * 4);

            // Verifica o checksum
            uint16_t checksum_recebido = udp_payload->checksum;
            uint16_t checksum_calculado;
            udp_payload->checksum = 0;
            checksum_calculado = checksum(udp_payload, ntohs(udp_payload->comprimento));

            // Verifica se há erro de integridade
            int integrity_error = 0;
            if (checksum_recebido != checksum_calculado || (udp_payload->flags & FLAG_ERR)) {
                integrity_error = 1;
                printf("Erro de integridade detectado no pacote de sequência %d\n", udp_payload->seq_num);
            }

            printf("Pacote recebido com sequência %d\n", udp_payload->seq_num);
            printf("Dados: %s\n", udp_payload->dados);

            // Decide se envia ACK ou NACK
            if (integrity_error || udp_payload->seq_num != expected_seq) {
                // Envia NACK
                if (nack_packet == udp_payload->seq_num) {
                    printf("Enviando NACK para sequência %d\n", udp_payload->seq_num);
                    // Prepara o NACK
                    struct udp_simulado ack_packet;
                    ack_packet.porta_origem = htons(PORTA_SERVIDOR);
                    ack_packet.porta_destino = udp_payload->porta_origem;
                    ack_packet.comprimento = htons(sizeof(struct udp_simulado) - TAMANHO_DADOS);
                    ack_packet.seq_num = 0;
                    ack_packet.ack_num = udp_payload->seq_num;
                    ack_packet.flags = FLAG_NACK;
                    ack_packet.window_size = recv_window;
                    ack_packet.checksum = 0;
                    ack_packet.checksum = checksum(&ack_packet, ntohs(ack_packet.comprimento));

                    // Envia o NACK
                    if (sendto(sock, &ack_packet, ntohs(ack_packet.comprimento), 0, (struct sockaddr *)&cliente, tamanho_cliente) < 0) {
                        perror("Erro ao enviar NACK");
                    }
                }
            } else {
                // Envia ACK se não for o pacote que não será confirmado
                if (ack_loss_packet != udp_payload->seq_num) {
                    printf("Enviando ACK para sequência %d\n", udp_payload->seq_num);
                    // Prepara o ACK
                    struct udp_simulado ack_packet;
                    ack_packet.porta_origem = htons(PORTA_SERVIDOR);
                    ack_packet.porta_destino = udp_payload->porta_origem;
                    ack_packet.comprimento = htons(sizeof(struct udp_simulado) - TAMANHO_DADOS);
                    ack_packet.seq_num = 0;
                    ack_packet.ack_num = udp_payload->seq_num;
                    ack_packet.flags = FLAG_ACK;
                    ack_packet.window_size = recv_window;

                    // Simula erro de integridade no ACK
                    if (error_ack_packet == udp_payload->seq_num) {
                        ack_packet.flags |= FLAG_ERR;
                        printf("Inserindo erro de integridade no ACK para sequência %d\n", udp_payload->seq_num);
                    }

                    ack_packet.checksum = 0;
                    ack_packet.checksum = checksum(&ack_packet, ntohs(ack_packet.comprimento));

                    // Envia o ACK
                    if (sendto(sock, &ack_packet, ntohs(ack_packet.comprimento), 0, (struct sockaddr *)&cliente, tamanho_cliente) < 0) {
                        perror("Erro ao enviar ACK");
                    } else {
                        // Atualiza o número de sequência esperado
                        expected_seq++;
                    }
                } else {
                    printf("Não enviando ACK para sequência %d conforme solicitado\n", udp_payload->seq_num);
                }
            }
        }

        // Pequena pausa para evitar uso excessivo de CPU
        usleep(100000);
    }

    close(sock);
    return 0;
}
