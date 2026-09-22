import socket
# Crear el socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# '0.0.0.0' permite escuchar peticiones de cualquier equipo en la red local
ip_local = '0.0.0.0' 
puerto = 5000
# Vincular el socket a la IP y puerto
s.bind((ip_local, puerto))
print(f"Servidor escuchando en el puerto {puerto}...")
while True:
    # 1. Recibir el mensaje del emisor (bloquea hasta que llega algo)
    mensaje, direccion = s.recvfrom(1024)
    print(f"Mensaje recibido de {direccion}: {mensaje.decode('utf-8')}")

    # 2. Enviar respuesta de vuelta al emisor
    respuesta = "Mensaje recibido correctamente"
    s.sendto(respuesta.encode('utf-8'), direccion)
