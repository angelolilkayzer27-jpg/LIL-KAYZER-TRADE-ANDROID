# LIL KAYZER TRADE para Android — proyecto APK

Este es el **código fuente** de una adaptación Android con Kivy. No es un APK ya compilado. Se incluye una automatización de GitHub Actions para intentar generar el APK en la nube sin instalar Android SDK en el teléfono.

## Funciones preparadas
- Las 10 estrategias del proyecto original y sus indicadores EMA, RSI, ATR, MACD, ADX y SAR.
- Interfaz Android adaptable, selección de temporalidad 1/2/5/10 minutos y expiración sugerida.
- Conexión en hilo separado y escaneo periódico de activos que la API reporte abiertos.
- Panel de señal, lista de señales recientes y filtros básicos Forex/OTC.
- Botón para abrir la sala oficial de IQ Option para que la operación sea manual. La aplicación no envía órdenes.

## Crear el APK usando GitHub desde un PC o teléfono

1. Descarga y descomprime `LIL_KAYZER_TRADE_ANDROID_APK_PROJECT.zip`.
2. En GitHub, crea un repositorio nuevo, por ejemplo `LIL-KAYZER-TRADE-ANDROID`.
3. Sube **todo el contenido de la carpeta** al repositorio, incluyendo la carpeta oculta `.github/workflows/build-apk.yml`. Si usas la web móvil, quizá sea más sencillo subir los archivos desde un navegador en modo escritorio o desde un PC.
4. Abre la pestaña **Actions** del repositorio y selecciona **Build LIL KAYZER TRADE APK**.
5. Pulsa **Run workflow** y confirma. También se inicia al subir cambios a la rama `main` o `master`.
6. Espera a que termine el trabajo `build-android`. Si aparece verde, abre la ejecución y busca **Artifacts**.
7. Descarga `LIL-KAYZER-TRADE-Android-APK`, descomprímelo y copia el `.apk` a tu Android para instalarlo.

Si la compilación falla, abre el trabajo y copia el primer error de la sección **Build debug APK**. La automatización permite construirlo, pero no garantiza que las dependencias de IQ Option sean compatibles con Android.

## Limitaciones importantes
1. `iqoptionapi` es una biblioteca no oficial y su compatibilidad con Buildozer/Android no está garantizada. Puede que el primer intento de compilación necesite ajustes.
2. El escaneo consulta velas aproximadamente cada 3 segundos; no es un feed tick-a-tick garantizado. El rendimiento depende de la conexión y de los límites de la API.
3. El botón abre la sala oficial `https://iqoption.com/traderoom`; no hay un enlace profundo por activo verificado. Debes buscar el activo de la señal y confirmar manualmente.
4. El programa solicita cambiar a `PRACTICE` después de conectar, como hacía el original. Verifica la cuenta en IQ Option antes de operar. No compartas credenciales por chat.
5. Los porcentajes son puntuaciones heurísticas de indicadores, no probabilidades estadísticas de ganar ni garantía de rentabilidad.
6. El proyecto no ha sido probado todavía contra una sesión real de IQ Option en un dispositivo Android.

## Seguridad
Introduce las credenciales únicamente en tu dispositivo. No las guardes en el repositorio, no las incluyas en capturas y no las compartas por chat. Prueba primero con una cuenta demo.
