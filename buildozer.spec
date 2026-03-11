[app]

# (str) Title of your application
title = projek1

# (str) Package name
package.name = projek1

# (str) Package domain (needed for android/ios packaging)
package.domain = org.ataraxymafia

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let everything)
source.include_exts = py,png,jpg,kv,atlas,txt

# (str) Application versioning
version = 0.1

# (list) Requirements (must be python modules)
requirements = python3,kivy

# (str) Orientation of the application (portrait/landscape)
orientation = portrait

# (str) OSX specific python version
osx.python_version = 3

# (str) OSX specific kivy version
osx.kivy_version = 2.2.1

# (bool) Enable fullscreen
fullscreen = 0

# ----- Android specific -----
android.accept_sdk_license = True
android.sdk_accept_license = True
android.build_tools_version = 34.0.0

# (int) Android API level to use
android.api = 33

# (int) Minimum API required
android.minapi = 24

# (str) Android NDK version
android.ndk = 25b

# (bool) Enable AndroidX
android.enable_androidx = True

# (list) Permissions
android.permissions = INTERNET

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (bool) Warn if root is used
warn_on_root = 1
