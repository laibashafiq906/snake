[app]
title = Advanced Snake Game
package.name = advancedsnake
package.domain = org.snakegame
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3
version = 1.0
requirements = python3,kivy,kivymd,android,jnius,https://github.com/MichaelStott/KivMob/archive/refs/heads/master.zip,plyer,requests,pillow
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

[android]
api = 31
ndk = 25b
private_storage = True
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-8134227271086623~8232284552
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
android.arch = armeabi-v7a
android.enable_androidx = True
android.minapi = 21
android.ndk_api = 21
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.0.0
p4a.bootstrap = sdl2
p4a.branch = master
