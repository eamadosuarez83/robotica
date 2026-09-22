# Recursos del curso

- `esquemas/`: fuente de cada figura (`.dot` de Graphviz o `.py` con schemdraw/Matplotlib).
- `imagenes/`: figuras generadas, en SVG siempre que se pueda.

Nunca se sube una imagen sin su fuente. La fuente y la imagen tienen el mismo nombre; cambia solo la extensión.

## Regenerar

```
$ dot -Tsvg esquemas/NOMBRE.dot -o imagenes/NOMBRE.svg
$ python esquemas/NOMBRE.py        # cada script guarda su imagen en imagenes/
```

## Convenciones de dibujo

- Ejes: **x rojo, y verde, z azul**, siempre dextrógiros.
- Ángulos positivos en sentido antihorario, con flecha curva.
- Texto de las figuras en español.
