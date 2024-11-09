#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <netinet/ip.h>
#include <time.h>
#include <fcntl.h>
#include <sys/select.h>

#define TAMANHO_BUFFER 4096
#define TAMANHO_DADOS 512
#define PORTA_DESTINO 8080
#define TIMEOUT_SEC 2  // Timeout for retransmission

// Flags
#define FLAG_ACK 0x1
#define FLAG_NACK 0x2
#define FLAG_SYN 0x4
#define FLAG_FIN 0x8
#define FLAG_ERR 0x10  // For error simulation

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

int main() {
    struct sockaddr_in destino;
    int sock;
    char pacote[4096];
    struct iphdr *ip_header = (struct iphdr *)pacote;
    struct udp_simulado *udp_payload = (struct udp_simulado *)(pacote + sizeof(struct iphdr));
    socklen_t tamanho_destino;
    int num_pacotes, i, erro_pacote;
    uint32_t seq_num = 0;
    uint16_t cwnd = 1;  // Congestion window
    uint16_t ssthresh = 8;  // Slow start threshold
    char mensagem[TAMANHO_DADOS];
    fd_set read_fds;
    struct timeval timeout;
    int bytes_recebidos;
    char buffer_recebido[TAMANHO_BUFFER];
    struct sockaddr_in origem;
    socklen_t tamanho_origem;
    int ack_expected = 0;

    // Cria um socket RAW
    sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (sock < 0) {
        perror("Erro ao criar socket");
        return 1;
    }

    // Habilita a inclusão do cabeçalho IP manualmente
    int optval = 1;
    if (setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &optval, sizeof(optval)) < 0) {
        perror("Erro ao configurar IP_HDRINCL");
        return 1;
    }

    // Configura o socket como não-bloqueante
    set_nonblocking(sock);

    // Preenche a estrutura de destino
    destino.sin_family = AF_INET;
    destino.sin_port = htons(PORTA_DESTINO);
    destino.sin_addr.s_addr = inet_addr("127.0.0.1");

    printf("Digite o número de pacotes a enviar: ");
    scanf("%d", &num_pacotes);
    getchar();  // Limpa o buffer do stdin

    printf("Deseja inserir um erro de integridade em algum pacote? (Digite o número do pacote ou 0 para nenhum): ");
    scanf("%d", &erro_pacote);
    getchar();  // Limpa o buffer do stdin

    for (i = 0; i < num_pacotes; i++) {
        memset(pacote, 0, sizeof(pacote));  // Limpa o pacote

        // Preenche os dados
        snprintf(mensagem, TAMANHO_DADOS, "Pacote número %d", i + 1);
        strcpy(udp_payload->dados, mensagem);

        // Preenche o cabeçalho do nosso "UDP" simulado
        udp_payload->porta_origem = htons(12345);
        udp_payload->porta_destino = htons(PORTA_DESTINO);
        udp_payload->comprimento = htons(sizeof(struct udp_simulado) - TAMANHO_DADOS + strlen(udp_payload->dados));
        udp_payload->seq_num = seq_num;
        udp_payload->ack_num = 0;
        udp_payload->flags = 0;
        udp_payload->window_size = cwnd;

        // Simula erro de integridade se for o pacote escolhido
        if (i + 1 == erro_pacote) {
            udp_payload->flags |= FLAG_ERR;
            printf("Inserindo erro de integridade no pacote %d\n", i + 1);
        }

        // Calcula o checksum
        udp_payload->checksum = 0;
        udp_payload->checksum = checksum(udp_payload, ntohs(udp_payload->comprimento));

        // Preenche o cabeçalho IP
        ip_header->ihl = 5;
        ip_header->version = 4;
        ip_header->tos = 0;
        int udp_len = ntohs(udp_payload->comprimento);
        ip_header->tot_len = htons(sizeof(struct iphdr) + udp_len);
        ip_header->id = htonl(54321 + i);
        ip_header->frag_off = 0;
        ip_header->ttl = 64;
        ip_header->protocol = IPPROTO_RAW;
        ip_header->check = 0;
        ip_header->saddr = inet_addr("127.0.0.1");
        ip_header->daddr = inet_addr("127.0.0.1");
        ip_header->check = checksum((unsigned short *)pacote, sizeof(struct iphdr));

        // Envia o pacote via socket RAW
        if (sendto(sock, pacote, ntohs(ip_header->tot_len), 0, (struct sockaddr *)&destino, sizeof(destino)) < 0) {
            perror("Erro ao enviar pacote");
            return 1;
        }

        printf("Pacote %d enviado com sequência %d\n", i + 1, seq_num);

        // Espera pelo ACK
        ack_expected = seq_num;
        seq_num++;  // Incrementa o número de sequência para o próximo pacote

        int ack_received = 0;
        int retransmit = 0;
        while (!ack_received) {
            // Configura o timeout
            FD_ZERO(&read_fds);
            FD_SET(sock, &read_fds);
            timeout.tv_sec = TIMEOUT_SEC;
            timeout.tv_usec = 0;

            int activity = select(sock + 1, &read_fds, NULL, NULL, &timeout);

            if (activity > 0 && FD_ISSET(sock, &read_fds)) {
                // Recebe o ACK
                memset(buffer_recebido, 0, TAMANHO_BUFFER);
                tamanho_origem = sizeof(origem);
                bytes_recebidos = recvfrom(sock, buffer_recebido, TAMANHO_BUFFER, 0, (struct sockaddr *)&origem, &tamanho_origem);
                if (bytes_recebidos > 0) {
                    struct iphdr *ip_header_resp = (struct iphdr *)buffer_recebido;
                    struct udp_simulado *udp_resp = (struct udp_simulado *)(buffer_recebido + ip_header_resp->ihl * 4);

                    // Verifica se é um ACK
                    if (udp_resp->flags & FLAG_ACK) {
                        if (udp_resp->ack_num == ack_expected) {
                            printf("ACK recebido para sequência %d\n", udp_resp->ack_num);
                            ack_received = 1;

                            // Atualiza a janela de congestionamento (Exemplo simples)
                            if (cwnd < ssthresh) {
                                cwnd *= 2;  // Crescimento exponencial
                            } else {
                                cwnd += 1;  // Crescimento linear
                            }
                        } else {
                            printf("ACK recebido para sequência inesperada %d\n", udp_resp->ack_num);
                        }
                    } else if (udp_resp->flags & FLAG_NACK) {
                        printf("NACK recebido para sequência %d. Retransmitindo...\n", udp_resp->ack_num);
                        ack_received = 0;
                        retransmit = 1;
                        break;
                    }
                }
            } else {
                // Timeout
                printf("Timeout aguardando ACK para sequência %d. Retransmitindo...\n", ack_expected);
                retransmit = 1;
                break;
            }
        }

        if (retransmit) {
            // Reduz a janela de congestionamento (Exemplo simples)
            ssthresh = cwnd / 2;
            cwnd = 1;
            seq_num = ack_expected;  // Reenvia o pacote com o mesmo número de sequência
            i--;  // Decrementa i para reenvio
        }
    }

    close(sock);
    return 0;
}
