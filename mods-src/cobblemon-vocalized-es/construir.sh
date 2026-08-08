#!/usr/bin/env bash
# Reconstruye Cobblemon: Vocalized en español desde cero.
#
# Uso:  JDK21=/ruta/al/jdk-21  ./construir.sh
#
# El modelo de voz (58 MB) no está en el repositorio: se descarga aquí.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRABAJO="${AQUI}/build"
UPSTREAM="https://gitlab.com/cable-mc/cobblemon-vocalized.git"
MODELO_URL="https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
MODELO_DIR="vosk-model-small-es-0.42"

if [ -z "${JDK21:-}" ]; then
	echo "Falta JDK21. Gradle necesita Java 21; con Java 17 falla al resolver unpick." >&2
	echo "Ejemplo: JDK21=/c/jdks/jdk-21 ./construir.sh" >&2
	exit 1
fi

rm -rf "${TRABAJO}"
mkdir -p "${TRABAJO}"
cd "${TRABAJO}"

echo "==> Clonando upstream"
git clone --depth 1 "${UPSTREAM}" src
cd src

echo "==> Aplicando cambios en español"
git apply "${AQUI}/espanol.patch"

echo "==> Descargando el modelo de voz español"
curl -sL -o modelo.zip "${MODELO_URL}"
unzip -q modelo.zip

# Las rutas de recursos de Minecraft sólo admiten [a-z0-9/._-]: un fichero con mayúsculas no
# aparece en el listado de recursos y el mod se queda mudo sin dar ningún error. Vosk los
# distribuye como Gr.fst / HCLr.fst / README, así que hay que pasarlos a minúscula.
DESTINO="common/src/main/resources/assets/cobblemon_vocalized/models/es_es"
mkdir -p "${DESTINO}"
cp -r "${MODELO_DIR}"/* "${DESTINO}/"
mv "${DESTINO}/graph/Gr.fst"   "${DESTINO}/graph/gr.fst"
mv "${DESTINO}/graph/HCLr.fst" "${DESTINO}/graph/hclr.fst"
mv "${DESTINO}/README"         "${DESTINO}/readme"

echo "==> Compilando"
# -Dorg.gradle.java.home se pasa a propósito: ~/.gradle/gradle.properties puede fijar un JDK 17
# global (IntelliJ lo hace) que pisaría a JAVA_HOME.
./gradlew :fabric:remapJar --console=plain --no-daemon "-Dorg.gradle.java.home=${JDK21}"

JAR=$(find fabric/build/libs -name "*-unspecified.jar" | head -1)
cp "${JAR}" "${AQUI}/../../client-pack/local-mods/cobblemon_vocalized-es-1.0.0.jar"
echo "==> Listo: client-pack/local-mods/cobblemon_vocalized-es-1.0.0.jar"
