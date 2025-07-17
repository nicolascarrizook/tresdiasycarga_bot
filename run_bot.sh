#!/bin/bash
# Script mejorado para iniciar el bot del Sistema Mayra

echo "🤖 Sistema Mayra - Bot de Nutrición"
echo "==================================="
echo ""

# Verificar si hay otras instancias ejecutándose
echo "🔍 Verificando instancias previas..."
PIDS=$(ps aux | grep -E "python.*bot" | grep -v grep | awk '{print $2}')

if [ ! -z "$PIDS" ]; then
    echo "⚠️  Encontradas instancias previas del bot"
    echo "🧹 Limpiando procesos..."
    for PID in $PIDS; do
        kill -9 $PID 2>/dev/null
        echo "   ✅ Proceso $PID terminado"
    done
    echo "⏳ Esperando 3 segundos..."
    sleep 3
fi

echo ""
echo "🚀 Iniciando bot..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el bot mejorado
python3 bot_mayra.py

# Si el bot termina, mostrar mensaje
echo ""
echo "👋 Bot detenido"