[app]
title = LIL KAYZER TRADE
package.name = lilkayzertrade
package.domain = com.lilkayzer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,md
version = 3.10
requirements = python3,kivy,requests,websocket-client,protobuf,https://github.com/Luis-Silva/iqoptionapi/archive/refs/heads/master.zip
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.ndk = 25b
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True


[buildozer]
log_level = 2
warn_on_root = 1
