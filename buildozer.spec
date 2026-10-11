[app]
title = LIL KAYZER TRADE
package.name = lilkayzertrade
package.domain = com.lilkayzer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,md
source.exclude_dirs = .buildozer,bin,__pycache__,tests,.git
version = 3.1.1

# Python 3.12 is the stable line supported by the p4a master branch used here.
# hostpython3 MUST match python3 exactly to avoid mixed-host/runtime builds.
requirements = python3==3.12.9,hostpython3==3.12.9,kivy==2.3.1,requests==2.32.4,websocket-client==0.56.0,my-iqoptionapi==7.1.2

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
