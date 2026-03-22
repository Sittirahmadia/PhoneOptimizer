[app]

# App info
title = Phone Optimizer
package.name = phoneoptimizer
package.domain = org.optimizer

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

# Requirements
requirements = python3,kivy==2.3.0,pyjnius,android

# Orientation
orientation = portrait

# Android permissions
android.permissions = WRITE_SETTINGS,WRITE_SECURE_SETTINGS,CHANGE_NETWORK_STATE,CHANGE_WIFI_STATE,ACCESS_NETWORK_STATE,VIBRATE

# Min Android SDK
android.minapi = 26
android.sdk = 33
android.ndk = 25b
android.ndk_api = 26

# Architecture
android.archs = arm64-v8a, armeabi-v7a

# Fullscreen
fullscreen = 0

# Icons (opsional — ganti dengan file kamu)
# icon.filename = %(source.dir)s/icon.png

# Build config
android.allow_backup = True
android.gradle_dependencies =

[buildozer]
log_level = 2
warn_on_root = 1
