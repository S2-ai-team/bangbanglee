[app]

title = STT Summary App
package.name = sttsummary
package.domain = org.example
source.dir = .
source.include_exts = py,html,json
version = 1.0
requirements = kivy,kivy_garden.webview,sounddevice,speechrecognition,scipy,numpy,requests
android.permissions = INTERNET,RECORD_AUDIO
android.add_assets = html/,json/

[buildozer]
log_level = 2
warn_on_root = 1

[app.android]
android.minapi = 21
android.ndk = 23b
android.api = 33
android.archs = armeabi-v7a, arm64-v8a
android.gradle_dependencies = androidx.webkit:webkit:1.4.0

[app.android.packaging]
extra_pyjnius_args = -Xmx4096m
