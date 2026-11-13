"""
Carga del crucigrama SST de 20 palabras y utilidades de validacion.
El layout fue generado por scripts/generar_crucigrama.py y se almacena como JSON.
"""
from __future__ import annotations
import json
import os
from functools import lru_cache


_LAYOUT_PATH = os.path.join(os.path.dirname(__file__), "crucigrama_layout.json")


@lru_cache(maxsize=1)
def cargar_layout() -> dict:
    """Carga el layout del crucigrama desde JSON."""
    with open(_LAYOUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def obtener_grid() -> list[list[str]]:
    """Retorna la matriz de letras ("" si celda bloqueada)."""
    layout = cargar_layout()
    return layout["grid"]


def obtener_palabras() -> list[dict]:
    """Retorna las 20 palabras con su pista, numero, direccion y posicion."""
    layout = cargar_layout()
    return layout["palabras"]


def obtener_dimensiones() -> tuple[int, int]:
    """Retorna (filas, columnas) del grid."""
    layout = cargar_layout()
    return layout["filas"], layout["cols"]


def obtener_numero_en_celda(fila: int, col: int) -> int:
    """Retorna el numero asignado a la celda si inicia palabra, 0 si no."""
    layout = cargar_layout()
    return layout["celdas_inicio"].get(f"{fila},{col}", 0)


def obtener_pistas_por_direccion() -> dict:
    """Retorna pistas separadas por direccion (H/V), ordenadas por numero."""
    palabras = obtener_palabras()
    horizontales = sorted([p for p in palabras if p["direccion"] == "H"], key=lambda x: x["numero"])
    verticales = sorted([p for p in palabras if p["direccion"] == "V"], key=lambda x: x["numero"])
    return {"horizontales": horizontales, "verticales": verticales}


def validar_respuestas(respuestas: dict) -> dict:
    """Compara las respuestas del visitante contra la solucion.
    respuestas: {"fila,col": "LETRA"}
    Retorna: {
        "palabras_correctas": [{"numero": N, "palabra": "...", "ok": True/False}],
        "aciertos": int,
        "total": 20,
        "completado": bool,
        "puntaje": int (0-100)
    }
    """
    layout = cargar_layout()
    grid_solucion = layout["grid"]
    palabras = layout["palabras"]

    resultado_palabras = []
    aciertos = 0

    for p in palabras:
        palabra_correcta = True
        letras_visitante = []
        for i, letra_esperada in enumerate(p["palabra"]):
            if p["direccion"] == "H":
                key = f"{p['fila']},{p['col'] + i}"
            else:
                key = f"{p['fila'] + i},{p['col']}"
            letra_ingresada = (respuestas.get(key, "") or "").upper().strip()
            letras_visitante.append(letra_ingresada)
            if letra_ingresada != letra_esperada:
                palabra_correcta = False
        if palabra_correcta:
            aciertos += 1
        resultado_palabras.append({
            "numero": p["numero"],
            "palabra": p["palabra"],
            "direccion": p["direccion"],
            "ok": palabra_correcta,
            "respuesta_visitante": "".join(letras_visitante),
        })

    total = len(palabras)
    completado = aciertos == total
    puntaje = int(round((aciertos / total) * 100)) if total else 0

    return {
        "palabras_correctas": resultado_palabras,
        "aciertos": aciertos,
        "total": total,
        "completado": completado,
        "puntaje": puntaje,
    }


def validar_celda_individual(respuestas: dict, fila: int, col: int) -> str:
    """Retorna 'correct' | 'incorrect' | '' para una celda dada."""
    grid = obtener_grid()
    if fila >= len(grid) or col >= len(grid[0]):
        return ""
    esperada = grid[fila][col]
    if not esperada:
        return ""
    ingresada = (respuestas.get(f"{fila},{col}", "") or "").upper().strip()
    if not ingresada:
        return ""
    return "correct" if ingresada == esperada else "incorrect"


def generar_resumen_visual() -> dict:
    """Genera un resumen del crucigrama (para mostrar info en la UI)."""
    layout = cargar_layout()
    palabras = layout["palabras"]
    return {
        "total_palabras": len(palabras),
        "horizontales": sum(1 for p in palabras if p["direccion"] == "H"),
        "verticales": sum(1 for p in palabras if p["direccion"] == "V"),
        "filas": layout["filas"],
        "cols": layout["cols"],
        "total_letras": sum(len(p["palabra"]) for p in palabras),
    }


def palabras_ordenadas() -> list[dict]:
    """Lista de palabras ordenadas por numero (para numeracion consistente)."""
    return sorted(obtener_palabras(), key=lambda p: p["numero"])
