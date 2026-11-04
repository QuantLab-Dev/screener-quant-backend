.PHONY: help setup install test run-screener anashei 

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help:
	@echo "Comandos disponibles para el Screener Cuantitativo:"
	@echo "  make setup        - Crea el entorno virtual e instala dependencias"
	@echo "  make install      - Instala dependencias desde requirements.txt"
	@echo "  make test         - Ejecuta la batería completa de tests unitarios (pytest)"
	@echo "  make run-screener - Ejecuta la ingesta, cálculo y exportación del reporte CSV"
	@echo "  make clean        - Limpia archivos temporales (.pyc, __pycache__, .pytest_cache)"
	@echo "  make anashei	    - Muestra un mensaje chupete"

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "Entorno virtual .venv configurado correctamente."

install:
	$(BIN)/pip install -r requirements.txt

test:
	$(BIN)/pytest tests/ -v --cov=app

run-screener:
	$(BIN)/python main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage

anashei:
	@echo "Yo te vi te gusta la nait"