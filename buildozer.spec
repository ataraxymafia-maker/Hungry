[app]
title = projek1
package.name = projek1
package.domain = org.ataraxymafia

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.1
requirements = python3,kivy
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0

# Стабильная версия build-tools и принудительное принятие лицензий
android.build_tools_version = 34.0.0
android.sdk_accept_license = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
