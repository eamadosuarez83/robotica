"""Funciones propias para dibujar cuadriculas, vectores y marcos 2D.

Bloque 03 -- Matrices como transformaciones. Convencion del curso:
ejes x en rojo, y en verde (ver FILOSOFIA.md).
"""

from __future__ import annotations

import numpy as np

COLOR_X = "tab:red"
COLOR_Y = "tab:green"


def dibujar_cuadricula(ax, transformacion: np.ndarray | None = None,
                        rango: float = 3.0, paso: float = 1.0,
                        color: str = "tab:blue", alpha: float = 0.5) -> None:
    """Dibuja una cuadricula uniforme, opcionalmente deformada por una matriz 2x2.

    Si `transformacion` es None se dibuja la cuadricula sin deformar.
    """
    A = np.eye(2) if transformacion is None else np.asarray(transformacion, dtype=float)
    valores = np.arange(-rango, rango + paso, paso)

    for v in valores:
        # lineas verticales (x = v, y variando) y horizontales (y = v, x variando)
        finos = np.linspace(-rango, rango, 100)

        vert = np.vstack([np.full_like(finos, v), finos])
        vert_t = A @ vert
        ax.plot(vert_t[0], vert_t[1], color=color, alpha=alpha, lw=0.8)

        horiz = np.vstack([finos, np.full_like(finos, v)])
        horiz_t = A @ horiz
        ax.plot(horiz_t[0], horiz_t[1], color=color, alpha=alpha, lw=0.8)


def dibujar_vector(ax, vector: np.ndarray, origen: np.ndarray | None = None,
                    color: str = "k", etiqueta: str | None = None) -> None:
    """Dibuja una flecha desde `origen` (por defecto el origen) hasta `vector`."""
    origen = np.zeros(2) if origen is None else np.asarray(origen, dtype=float)
    vector = np.asarray(vector, dtype=float)
    ax.annotate(
        "", xy=tuple(origen + vector), xytext=tuple(origen),
        arrowprops=dict(arrowstyle="->", color=color, lw=2),
    )
    if etiqueta:
        pos = origen + vector
        ax.text(pos[0], pos[1], f"  {etiqueta}", color=color, fontsize=11)


def dibujar_marco2d(ax, transformacion: np.ndarray | None = None,
                     origen: np.ndarray | None = None, etiqueta: str = "") -> None:
    """Dibuja los ejes x (rojo) e y (verde) de un marco, transformados por una matriz."""
    A = np.eye(2) if transformacion is None else np.asarray(transformacion, dtype=float)
    origen = np.zeros(2) if origen is None else np.asarray(origen, dtype=float)

    dibujar_vector(ax, A[:, 0], origen=origen, color=COLOR_X, etiqueta=f"x{etiqueta}")
    dibujar_vector(ax, A[:, 1], origen=origen, color=COLOR_Y, etiqueta=f"y{etiqueta}")
