import sys
import subprocess

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 crear_issue.py <titulo> <cuerpo>")
        return

    titulo = sys.argv[1]
    cuerpo = sys.argv[2]
    
    # Configuración correcta con comillas para que actúe como String
    USUARIO = "FabrizioV22" 
    REPO_TARGET = f"{USUARIO}/proyecto-agentes-seguridad"

    try:
        # Ejecutamos gh pasándole explícitamente el entorno actual
        resultado = subprocess.run(
            ["gh", "issue", "create", "--repo", REPO_TARGET, "--title", titulo, "--body", cuerpo],
            capture_output=True, text=True, check=True
        )
        print(f"✅ Éxito! URL: {resultado.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error de subprocess. Código: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")

if __name__ == "__main__":
    main()