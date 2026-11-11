[app]
title = Калькулятор физики
package.name = physicscalc
package.domain = org.example
source.include_exts = py,png,jpg,kv,atlas,json,ico
requirements = python3,kivy==2.3.0,kivymd==1.2.0,Cython==0.29.33,pyjnius==1.5.0
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.ico
android.accept_sdk_license = True
android.ndk_api = 21
