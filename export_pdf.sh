#!/usr/bin/env bash
# Exporta los bloques del curso (y el libro completo) a PDF.
#
# Requiere: pandoc, TeX Live con lualatex, las fuentes DejaVu + Noto Color
# Emoji, y el binario `dot` de Graphviz si se regeneran los esquemas de
# recursos/esquemas/*.dot.
#
# Uso:
#   ./export_pdf.sh              # exporta cada bloque por separado + el libro completo
#   ./export_pdf.sh bloque_01_trigonometria_geometria_plano   # solo ese bloque

set -euo pipefail
cd "$(dirname "$0")"

OUT=pdf
mkdir -p "$OUT"

PANDOC_OPTS=(
  --pdf-engine=lualatex
  -V lang=es
  -V geometry:margin=2.5cm
  -V mainfont="DejaVu Serif"
  -V monofont="DejaVu Sans Mono"
  -V mainfontfallback="Noto Color Emoji:mode=harf"
  -V monofontfallback="Noto Color Emoji:mode=harf"
  -V documentclass=report
)

# ------------------------------------------------------------------ figuras
# Los .dot de Graphviz se convierten a SVG (para leer el Markdown en GitHub)
# y a PDF (vectorial, para LuaLaTeX, que no incrusta SVG directamente).
generar_figuras() {
  echo "Generando figuras..."
  (
    cd recursos/esquemas
    for f in *.dot; do
      [ -e "$f" ] || continue
      dot -Tsvg "$f" -o "../imagenes/${f%.dot}.svg"
      dot -Tpdf "$f" -o "../imagenes/${f%.dot}.pdf"
    done
  )
}

# Sustituye rutas .../imagenes/nombre.svg -> .pdf en una copia temporal, para
# que LuaLaTeX use el vectorial. Devuelve la ruta de la copia por stdout.
preparar_md() {
  local origen="$1"
  local copia
  copia="$(dirname "$origen")/.build-$(basename "$origen")"
  sed 's|\(recursos/imagenes/[A-Za-z0-9_-]*\)\.svg|\1.pdf|g' "$origen" > "$copia"
  echo "$copia"
}

exportar_bloque() {
  local archivo="$1"
  local base copia
  base=$(basename "$archivo" .md)
  copia=$(preparar_md "$archivo")
  echo "-> $OUT/$base.pdf"
  pandoc "$copia" -o "$OUT/$base.pdf" \
    --resource-path=.:bloques \
    "${PANDOC_OPTS[@]}"
  rm -f "$copia"
}

generar_figuras

if [ $# -ge 1 ]; then
  for nombre in "$@"; do
    exportar_bloque "bloques/${nombre}.md"
  done
  exit 0
fi

echo "Exportando bloques individuales..."
for f in bloques/bloque_*.md; do
  exportar_bloque "$f"
done

echo "Exportando libro completo..."
COPIAS=()
for f in FILOSOFIA.md ESTRUCTURA.md bloques/bloque_*.md; do
  COPIAS+=("$(preparar_md "$f")")
done
pandoc "${COPIAS[@]}" \
  -o "$OUT/curso_robotica_completo.pdf" \
  --resource-path=.:bloques \
  --toc \
  "${PANDOC_OPTS[@]}"
rm -f "${COPIAS[@]}"
echo "-> $OUT/curso_robotica_completo.pdf"

echo "Listo. PDFs en $OUT/ (carpeta ignorada por git)."
