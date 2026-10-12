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

mensagem = input(str("Mensagem a ser enviada ao servidor. Envie 'Fechar' para encerrar a conexão:   "))

while mensagem != "Fechar" and mensagem != "fechar":
    # Envia uma mensagem ao servidor.
    client.sendall(mensagem.encode())

    # Recebe até 1024 bytes do servidor.
    data = client.recv(1024)

    print("Resposta:", data.decode())
    mensagem = input(str("Mensagem a ser enviada ao servidor. Envie 'Fechar' para encerrar a conexão:   "))

# Envia uma mensagem ao servidor.
client.sendall(mensagem.encode())

# Recebe até 1024 bytes do servidor.
data = client.recv(1024)

# Fecha a conexão.
client.close()

# IPv6:
# - troque AF_INET por AF_INET6
# - troque 127.0.0.1 por ::1