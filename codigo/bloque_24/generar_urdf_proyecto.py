"""Entregable 4: modelo CAD parametrico (build123d) y URDF del brazo
del proyecto (prototipo_4gdl), generalizando el patron del Bloque 21
a 4 articulaciones.

Correr con:
    python codigo/bloque_24/generar_urdf_proyecto.py
"""

import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

import numpy as np
from build123d import Box, BuildPart

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.orientacion import mat2rpy  # noqa: E402
from robotica.rotaciones import rotx, rotz  # noqa: E402
from modelo_proyecto import DH, LONGITUDES  # noqa: E402

DENSIDAD_ALUMINIO = 2700.0
ANCHO, ALTO = 0.02, 0.015


def construir_eslabon(largo):
    largo = max(largo, 0.01)   # el eslabón 4 (pinza, 2 cm) sigue siendo una caja válida
    with BuildPart() as eslabon:
        Box(largo, ANCHO, ALTO)
    return eslabon.part


def propiedades(part, densidad=DENSIDAD_ALUMINIO):
    masa = part.volume * densidad
    tensor = np.array(part.matrix_of_inertia) * densidad
    return masa, tensor


def origen_urdf(d_prev, a_prev, alpha_prev, theta_offset):
    """Reindexación DH-estándar -> URDF (Bloque 21, Tema 21.4), generalizada:

    la rotación fija del origen es Rx(alpha_prev) @ Rz(theta_offset) (en
    ese orden -- Bloque 03, Tema 3.2: el orden de composición importa).
    Cuando alpha_prev y theta_offset son AMBOS distintos de cero (el
    caso de prototipo_4gdl, a diferencia de curso_3gdl en el Bloque 21,
    donde todos los theta_offset eran 0 y el orden no se notaba), esa
    rotación no coincide con la convención rpy de URDF
    (R = Rz(yaw)·Ry(pitch)·Rx(roll)) tomando roll=alpha_prev,
    yaw=theta_offset directamente -- hay que convertir la matriz
    combinada a RPY de verdad con robotica.orientacion.mat2rpy (Bloque 09).
    """
    R = rotx(alpha_prev) @ rotz(theta_offset)
    roll, pitch, yaw = mat2rpy(R)
    return (a_prev, 0, d_prev), (roll, pitch, yaw)


def construir_urdf():
    robot = Element("robot", name="prototipo_4gdl")
    SubElement(robot, "link", name="base_link")

    d_prev, a_prev, alpha_prev = 0.0, 0.0, 0.0
    padre = "base_link"
    for i, (theta_off, d_i, a_i, alpha_i, tipo) in enumerate(DH, start=1):
        largo = LONGITUDES[i - 1]
        part = construir_eslabon(largo)
        masa, tensor = propiedades(part)

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

    tcp = SubElement(robot, "link", name="tcp")
    joint_tcp = SubElement(robot, "joint", name="joint_tcp", type="fixed")
    SubElement(joint_tcp, "origin", xyz=f"{a_prev} 0 {d_prev}", rpy=f"{alpha_prev} 0 0")
    SubElement(joint_tcp, "parent", link=padre)
    SubElement(joint_tcp, "child", link="tcp")

    return robot


if __name__ == "__main__":
    robot = construir_urdf()
    ruta = Path(__file__).parent / "prototipo_4gdl.urdf"
    xml_str = minidom.parseString(tostring(robot)).toprettyxml(indent="  ")
    ruta.write_text(xml_str, encoding="utf-8")
    print(f"URDF guardado en: {ruta}")
