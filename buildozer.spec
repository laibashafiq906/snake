[app]

# (str) Title of your application
title = Advanced Snake Game

# (str) Package name
package.name = advancedsnake

# (str) Package domain (needed for android/ios packaging)
package.domain = org.snakegame

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,wav,mp3

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
requirements = python3,kivy,kivymd,kivmob,plyer,requests,pillow

# (str) Presplash of the application
presplash.filename = assets/images/presplash.png

# (str) Icon of the application
icon.filename = assets/images/icon.png

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

[android]

# (str) Android SDK version to use
api = 30

# (str) Android NDK version to use
ndk = 23b

# (bool) Use --private data storage (True) or --dir public storage (False)
private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
ndk_dir = 

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
sdk_dir = 

# (list) Android application meta-data to set (key=value format)
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-8134227271086623~8232284552

# (list) Android permissions to add
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a

# (list) Gradle dependencies to add
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.0.0

# (str) Android manifest additions
android.add_src = java/

[buildozer:1]
line_length = 100 