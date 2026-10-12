# LIL KAYZER TRADE para Android — proyecto APK corregido

He corregido el proyecto para que el flujo de compilación Android sea reproducible y no dependa de una caché anterior dañada.

## Correcciones aplicadas

- Se eliminó la selección implícita de Python 3.14 que estaba provocando fallos en la fase de compilación de Python/p4a.
- Kivy queda fijado a **2.3.1**.
- Buildozer queda fijado a **1.6.0** y Cython a **0.29.34** en GitHub Actions.
- Android NDK queda fijado a **28c** y arquitectura a **arm64-v8a**.
- Se eliminó `protobuf` del proyecto porque `main.py` no lo utiliza y una dependencia innecesaria puede introducir fallos de compilación.
- Se usa `my-iqoptionapi 7.1.2`, que proporciona el paquete importable `iqoptionapi`; el paquete `iqoptionapi` de PyPI que tiene ese nombre es una versión antigua 0.5 y no corresponde a la API moderna usada por este proyecto.
- Se eliminó la estrategia anterior de “compilar, parchear `remote_debugging.c` y recompilar”; ahora se usa una combinación de versiones coherente.
- La acción de GitHub borra `.buildozer`, `bin` y `~/.buildozer` antes de compilar para evitar reutilizar artefactos corruptos.
- La acción falla explícitamente si Buildozer termina sin generar un `.apk`.
- Se agregó validación de sintaxis Python y pruebas de las 10 estrategias antes de construir.
- El escáner ahora recoge todos los mercados que `get_all_open_time()` reporte como abiertos, no solo `turbo` y `binary`.
- Se usa el timestamp del servidor del broker cuando la biblioteca lo expone.
- Se agregó comprobación/reconexión de la sesión durante el escaneo.
- Se mejoró la apertura de la sala de IQ Option en Android mediante `Intent`.
- Las credenciales solo permanecen en memoria durante la ejecución; no se escriben en archivos.

## Funcionalidad conservada

- Interfaz Kivy vertical.
- Temporalidades 1, 2, 5 y 10 minutos.
- Las 10 estrategias existentes.
- EMA, RSI, ATR, MACD, ADX y SAR.
- Escaneo de activos abiertos.
- Panel de señal e historial.
- Filtros Forex/OTC.
- La aplicación sigue siendo de **señales/manual**: no se envían órdenes de compra/venta desde este APK.
- La cuenta solicitada al conectar es `PRACTICE`.

## Cómo generar el APK

1. Descomprime el ZIP y sube **el contenido de la carpeta `LIL_KAYZER_TRADE_ANDROID`** a la raíz del repositorio GitHub (la carpeta `.github` debe quedar en la raíz, no dentro de otra carpeta).
2. Usa la rama `main` o `master`.
3. Abre **Actions → Build LIL KAYZER TRADE APK → Run workflow**.
4. Espera a que el trabajo termine en verde.
5. En **Artifacts**, descarga `LIL-KAYZER-TRADE-Android-APK`.
6. Dentro encontrarás el `.apk` listo para instalar en un Android ARM64.

El flujo empieza desde cero, ejecuta pruebas de lógica y comprueba que se haya generado un APK. La captura solo muestra `exit code 100`, no el error original del compilador; por eso no se puede prometer una compilación sin errores hasta ver el registro completo de la tarea.

## Verificación local

Antes de subirlo se puede comprobar la sintaxis con:

```bash
python -m py_compile main.py
```

Las pruebas puras de indicadores se encuentran en `tests/test_logic.py` y no requieren Kivy para ejecutarse.

## Nota importante

La compilación de un APK y la conexión posterior con IQ Option son dos verificaciones diferentes. El proyecto queda preparado para una compilación limpia, pero ninguna revisión estática puede garantizar una sesión de broker real sin ejecutar el APK en un teléfono y probar la cuenta. No coloques credenciales en GitHub ni en el código fuente.
