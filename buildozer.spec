[app]
title = LIL KAYZER TRADE
package.name = lilkayzertrade
package.domain = com.lilkayzer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,md
source.exclude_dirs = .buildozer,bin,__pycache__,tests,.git
version = 3.1.4

# Deja que python-for-android seleccione su receta compatible de Python/hostpython.
# No fijar hostpython3 como dependencia de aplicación: lo gestiona p4a.
requirements = python3,kivy==2.3.1,requests==2.32.4,websocket-client==0.56.0,my-iqoptionapi==7.1.2

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 35
android.minapi = 23
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True
android.enable_androidx = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
