#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para capturar a posição atual do mouse.
Se executado com --json, imprime um JSON com as coordenadas.
Caso contrário, imprime uma mensagem amigável.
"""

import sys
import json
import argparse
import pyautogui

def main():
    parser = argparse.ArgumentParser(description='Captura posição do mouse')
    parser.add_argument('--json', action='store_true', help='Saída em formato JSON')
    args = parser.parse_args()

    x, y = pyautogui.position()

    if args.json:
        json.dump({'x': x, 'y': y}, sys.stdout)
    else:
        print(f"Posição atual do mouse: X={x}, Y={y}")

if __name__ == '__main__':
    main()