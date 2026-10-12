import socket

HOST = "127.0.0.1"
PORT = 38912

# Cria um socket TCP usando IPv4.
# AF_INET = IPv4
# SOCK_STREAM = TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associa o socket ao endereço IP e à porta.
server.bind((HOST, PORT))

# Coloca o socket em modo de escuta.
# O argumento 1 indica o tamanho da fila de conexões pendentes.
server.listen(1)

print("Servidor aguardando conexão...")

# Aguarda uma conexão e retorna:
# conn = socket para comunicação com o cliente
# addr = endereço IP e porta do cliente
conn, addr = server.accept()

print(f"Cliente conectado: {addr}")

# Recebe até 1024 bytes do cliente.
data = conn.recv(1024)

print("Recebido:", data.decode())

# Envia uma resposta ao cliente.
conn.sendall(b"Mensagem recebida!")

# Fecha a conexão com o cliente.
conn.close()

# Fecha o socket do servidor.
server.close()

# IPv6:
# - troque AF_INET por AF_INET6
# - troque 127.0.0.1 por ::1