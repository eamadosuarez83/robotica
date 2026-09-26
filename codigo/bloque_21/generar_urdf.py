"""Genera el URDF de curso_3gdl a partir de su tabla DH estandar
(Bloque 11), aplicando la reindexacion DH-estandar -> URDF verificada
en el Bloque 21, Tema 21.4: el origen del joint i usa d,a,alpha de la
fila ANTERIOR de la tabla DH (la misma reindexacion que separa DH
estandar de DH modificado, Bloque 11 Tema 11.6).

Correr con:
    python codigo/bloque_21/generar_urdf.py
"""

import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eslabon_parametrico import ANCHO, ALTO, DENSIDAD_ALUMINIO, L1, L2, L3, propiedades_fisicas, construir_eslabon  # noqa: E402

# Tabla DH estándar de curso_3gdl (Bloque 11): [theta_offset, d, a, alpha, tipo]
DH = [[0, L1, 0, np.pi / 2, 0], [0, 0, L2, 0, 0], [0, 0, L3, 0, 0]]
LONGITUDES = [L1, L2, L3]


def origen_urdf(d_prev, a_prev, alpha_prev, theta_offset):
    """rpy, xyz del <origin> de un joint (Bloque 21, Tema 21.4):
    Tz(d_prev) Tx(a_prev) Rx(alpha_prev) Rz(theta_offset)."""
    xyz = (a_prev, 0, d_prev)
    rpy = (alpha_prev, 0, theta_offset)
    return xyz, rpy


def construir_urdf():
    robot = Element("robot", name="curso_3gdl")

    base = SubElement(robot, "link", name="base_link")

    d_prev, a_prev, alpha_prev = 0.0, 0.0, 0.0
    padre = "base_link"
    for i, (theta_off, d_i, a_i, alpha_i, tipo) in enumerate(DH, start=1):
        largo = LONGITUDES[i - 1]
        part = construir_eslabon(largo)
        masa, com, tensor = propiedades_fisicas(part, DENSIDAD_ALUMINIO)

        nombre_link = f"eslabon_{i}"
        link = SubElement(robot, "link", name=nombre_link)
        inertial = SubElement(link, "inertial")
        SubElement(inertial, "origin", xyz=f"{largo/2} 0 0", rpy="0 0 0")
        SubElement(inertial, "mass", value=f"{masa:.6f}")
        SubElement(inertial, "inertia",
                   ixx=f"{tensor[0,0]:.8f}", ixy="0", ixz="0",
                   iyy=f"{tensor[1,1]:.8f}", iyz="0", izz=f"{tensor[2,2]:.8f}")

        joint = SubElement(robot, "joint", name=f"joint_{i}", type="revolute")
        xyz, rpy = origen_urdf(d_prev, a_prev, alpha_prev, theta_off)
        SubElement(joint, "origin", xyz=" ".join(f"{v:.6f}" for v in xyz),
                   rpy=" ".join(f"{v:.6f}" for v in rpy))
        SubElement(joint, "parent", link=padre)
        SubElement(joint, "child", link=nombre_link)
        SubElement(joint, "axis", xyz="0 0 1")
        SubElement(joint, "limit", lower="-3.1416", upper="3.1416", effort="10", velocity="5")

        d_prev, a_prev, alpha_prev = d_i, a_i, alpha_i
        padre = nombre_link

    # Marco final (Tema 21.4): el tramo fijo que queda tras el último joint.
    tcp = SubElement(robot, "link", name="tcp")
    joint_tcp = SubElement(robot, "joint", name="joint_tcp", type="fixed")
    SubElement(joint_tcp, "origin", xyz=f"{a_prev} 0 {d_prev}",
               rpy=f"{alpha_prev} 0 0")
    SubElement(joint_tcp, "parent", link=padre)
    SubElement(joint_tcp, "child", link="tcp")

    return robot


def guardar_urdf(robot, ruta):
    xml_str = minidom.parseString(tostring(robot)).toprettyxml(indent="  ")
    Path(ruta).write_text(xml_str, encoding="utf-8")


if __name__ == "__main__":
    robot = construir_urdf()
    ruta = Path(__file__).parent / "curso_3gdl.urdf"
    guardar_urdf(robot, ruta)
    print(f"URDF guardado en: {ruta}")
