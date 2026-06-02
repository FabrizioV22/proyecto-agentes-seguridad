import ollama
import subprocess
import json

def ejecutar_nmap(target):
    print(f"[*] Ejecutando Nmap real sobre {target}...")
    # Escaneamos específicamente los puertos de desarrollo y los estándar de apps web
    comando = ["nmap", "-p", "80,443,8080,11434,18789", target]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    return resultado.stdout

def agente_auditor_avanzado(objetivo):
    # 1. Ejecución física de la herramienta (Fase de Reconocimiento)
    salida_nmap = ejecutar_nmap(objetivo)
    
    # Imprimimos los logs crudos en la terminal para que TÚ verifiques el trabajo de la IA
    print("\n[LOG SISTEMA] Salida cruda de Nmap:")
    print(salida_nmap)
    print("-" * 50)
    
    # 2. El Cerebro procesa la información real
    prompt_sistema = (
        "Eres un experto en Penetration Testing. Analiza los resultados técnicos "
        "provistos, identifica los servicios expuestos y reporta vulnerabilidades potenciales."
    )
    
    prompt_usuario = f"""
    Analiza el siguiente escaneo de infraestructura:
    {salida_nmap}
    
    Si encuentras el puerto 11434 abierto, advierte que corresponde a la API de Ollama y que debe protegerse.
    """
    
    print("[+] Llama 3.1 procesando el reporte...")
    response = ollama.generate(model='llama3.1', system=prompt_sistema, prompt=prompt_usuario)
    
    print("\n================ REPORT DE AUDITORÍA REAL ================\n")
    print(response['response'])

if __name__ == "__main__":
    # Probamos apuntando al localhost
    agente_auditor_avanzado("127.0.0.1")
