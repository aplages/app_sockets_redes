import socket

HOST = "127.0.0.1"
PORT = 38912

# Cria um socket TCP usando IPv4.
# AF_INET = IPv4
# SOCK_STREAM = TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor.
# O endereço é formado por (IP, porta).
client.connect((HOST, PORT))

# Envia uma mensagem ao servidor.
client.sendall(b"Ola, servidor!")

# Recebe até 1024 bytes do servidor.
data = client.recv(1024)

print("Resposta:", data.decode())

# Fecha a conexão.
client.close()

# IPv6:
# - troque AF_INET por AF_INET6
# - troque 127.0.0.1 por ::1