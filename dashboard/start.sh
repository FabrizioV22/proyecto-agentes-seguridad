#!/bin/bash
# =============================================================
# 🛡️ Security Agents Dashboard - Script de Inicio
# =============================================================
# Inicia tanto el backend (FastAPI) como el frontend (Vite+React)
# =============================================================

set -e

PROJECT_DIR="/root/proyecto-agentes-seguridad"
DASHBOARD_DIR="$PROJECT_DIR/dashboard"
BACKEND_DIR="$DASHBOARD_DIR/backend"
FRONTEND_DIR="$DASHBOARD_DIR/frontend"
VENV_DIR="$PROJECT_DIR/venv-seguridad"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║   🛡️  Security Agents Dashboard - Iniciando...      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar que existan los directorios
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ No se encontró el directorio del backend: $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ No se encontró el directorio del frontend: $FRONTEND_DIR${NC}"
    exit 1
fi

# --- BACKEND ---
echo -e "${YELLOW}📦 Instalando dependencias del backend...${NC}"
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    pip install -q -r "$BACKEND_DIR/requirements.txt"
else
    echo -e "${YELLOW}⚠️  No se encontró venv, instalando globalmente...${NC}"
    pip install -q -r "$BACKEND_DIR/requirements.txt"
fi

echo -e "${GREEN}✅ Dependencias del backend instaladas${NC}"

# --- FRONTEND ---
echo -e "${YELLOW}📦 Instalando dependencias del frontend...${NC}"
cd "$FRONTEND_DIR"
npm install --silent
echo -e "${GREEN}✅ Dependencias del frontend instaladas${NC}"

# --- INICIAR SERVICIOS ---
echo ""
echo -e "${CYAN}🚀 Iniciando Backend (FastAPI en puerto 8000)...${NC}"
cd "$BACKEND_DIR"
if [ -d "$VENV_DIR" ]; then
    "$VENV_DIR/bin/python3" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
else
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
fi
BACKEND_PID=$!
echo -e "${GREEN}   Backend PID: $BACKEND_PID${NC}"

# Esperar un momento para que el backend inicie
sleep 2

echo -e "${CYAN}🚀 Iniciando Frontend (Vite en puerto 5173)...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}   Frontend PID: $FRONTEND_PID${NC}"

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║   ✅ Dashboard iniciado correctamente               ║"
echo "║                                                      ║"
echo "║   🌐 Frontend: http://localhost:5173                 ║"
echo "║   ⚙️  Backend:  http://localhost:8000                 ║"
echo "║   📡 API Docs: http://localhost:8000/docs            ║"
echo "║                                                      ║"
echo "║   Presiona Ctrl+C para detener ambos servicios       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Capturar Ctrl+C para matar ambos procesos
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Esperar a que los procesos terminen
wait
