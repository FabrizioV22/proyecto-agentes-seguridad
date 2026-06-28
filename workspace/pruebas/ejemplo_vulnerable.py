import subprocess
import pickle
import hashlib

# 1. Uso de eval (Inyección de código)
def ejecutar_comando_dinamico(entrada_usuario):
    # Bandit detectará B307 (uso de eval)
    return eval(entrada_usuario)

# 2. Ejecución de comandos del sistema con shell=True (Inyección de Comandos)
def hacer_ping(ip_destino):
    # Bandit detectará B602/B603 (ejecución de comandos por medio de shell externa)
    comando = f"ping -c 4 {ip_destino}"
    subprocess.run(comando, shell=True)

# 3. Deserialización insegura de objetos (RCE)
def deserializar_datos(datos_recibidos):
    # Bandit detectará B301 (uso inseguro del módulo pickle)
    return pickle.loads(datos_recibidos)

# 4. Criptografía débil / Obsoleta
def encriptar_contrasena(contrasena):
    # Bandit detectará B303 (uso de algoritmos inseguros MD5 / SHA1)
    hash_obj = hashlib.md5(contrasena.encode())
    return hash_obj.hexdigest()
