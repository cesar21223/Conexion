

import socket
import sys

def iniciar_cliente():
    ip_servidor = input("IP del servidor: ").strip()
    puerto = 5000
    apodo = input("Tu nombre de usuario: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip_servidor, puerto))
    except Exception as e:
        print(f"No se pudo conectar: {e}")
        return

    # Proceso de autenticación inicial (bloqueante al inicio)
    msg = sock.recv(1024).decode('utf-8')
    if msg == "SOLICITAR_NICKNAME":
        sock.send(apodo.encode('utf-8'))
        resp = sock.recv(1024).decode('utf-8')
        if not resp.startswith("OK"):
            print(f"Rechazado por el servidor: {resp}")
            sock.close()
            return

    # Configuramos el socket a MODO NO BLOQUEANTE para no usar hilos
    sock.setblocking(False)

    usuarios_activos = []
    print(f"\n=== SESIÓN INICIADA COMO: {apodo} ===")

    while True:
        # 1. Revisar si hay mensajes entrantes del servidor
        try:
            datos = sock.recv(1024).decode('utf-8')
            if datos:
                if datos.startswith("LISTA_USUARIOS:"):
                    raw = datos.split(":", 1)[1]
                    usuarios_activos = [u for u in raw.split(",") if u]
                elif datos.startswith("MENSAJE_PRIVADO:"):
                    _, emisor, mensaje = datos.split(":", 2)
                    print(f"\n>>> [Mensaje de {emisor}]: {mensaje}")
                elif datos.startswith("SISTEMA:"):
                    _, msg_sys = datos.split(":", 1)
                    print(f"\n[Aviso]: {msg_sys}")
        except BlockingIOError:
            # No hay mensajes nuevos en este instante, el programa continúa libremente
            pass
        except Exception:
            print("\nConexión con el servidor perdida.")
            break

        # 2. Menú de interacción
        print("\n--- MENÚ ---")
        print("1. Enviar mensaje")
        print("2. Ver usuarios en línea")
        print("3. Actualizar buzón de entrada")
        print("4. Salir")
        opcion = input("Opción: ").strip()

        if opcion == "1":
            destinatario = input("Destinatario: ").strip()
            if destinatario == apodo:
                print("No puedes enviarte mensajes a ti mismo.")
                continue
            
            mensaje = input(f"Mensaje para {destinatario}: ").strip()
            if mensaje:
                paquete = f"{destinatario}:{mensaje}"
                sock.send(paquete.encode('utf-8'))

        elif opcion == "2":
            print("\nUsuarios en línea:", ", ".join(usuarios_activos))

        elif opcion == "3":
            # Opción rápida para forzar la lectura del buffer sin enviar nada
            continue

        elif opcion == "4":
            print("Saliendo...")
            sock.close()
            sys.exit()

if __name__ == "__main__":
    iniciar_cliente()

