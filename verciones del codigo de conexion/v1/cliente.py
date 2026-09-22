import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip_destino = 'IP_DEL_RECEPTOR' # Reemplazar por la IP real

puerto = 5000
# 1. Envía el mensaje inicial

s.sendto(b"Hola, receptor", (ip_destino, puerto))

# 2. Se bloquea a la espera de la respuesta

respuesta, direccion = s.recvfrom(1024)

print(f"Respuesta de {direccion}: {respuesta.decode('utf-8')}") 
