[app]
title = Calendario
package.name = calendario
package.domain = org.calendario
source.dir = .
source.include_exts = py,html,css,js,png,webmanifest
source.exclude_dirs = instance,bin,.buildozer,__pycache__
version = 1.0
requirements = python3,flask==3.0.0,flask-sqlalchemy==3.1.1,sqlalchemy==2.0.23,flask-wtf==1.2.1,wtforms==3.1.1,werkzeug==3.0.1,jinja2==3.1.2,markupsafe==2.1.3,itsdangerous==2.1.2,click==8.1.7,blinker==1.7.0,six==1.16.0,typing_extensions==4.8.0,sqlite3
icon.filename = static/icona-512.png
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = webview
p4a.port = 5000

[buildozer]
log_level = 2
warn_on_root = 1
