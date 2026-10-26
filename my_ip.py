import socket

# Cria um socket UDP e conecta a um endereço externo (sem precisar de internet real)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    # Não precisa estar conectado; apenas define a rota
    s.connect(('10.255.255.255', 1))
    IP_local = s.getsockname()[0]
except Exception:
    IP_local = '127.0.0.1'
finally:
    s.close()

print(f"O IP da rede local é: {IP_local}")

