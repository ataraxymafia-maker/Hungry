[app]
title = projekt1
package.name = projekt1
package.domain = org.ataraxymafia

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.1
requirements = python3,kivy
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0

# Указываем стабильную версию build-tools
android.build_tools_version = 34.0.0
android.sdk_accept_license = True

[buildozer]
log_level = 2
warn_on_root = 1
