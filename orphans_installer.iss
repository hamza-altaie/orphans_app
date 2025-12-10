;-----------------------------
; إعدادات البرنامج
;-----------------------------
[Setup]
AppName=نظام كفالة الأيتام
AppVersion=1.0
; الأفضل نستخدم autopf حتى يختار Program Files المناسب تلقائياً
DefaultDirName={autopf}\OrphansApp
DefaultGroupName=نظام كفالة الأيتام
OutputBaseFilename=OrphansAppSetup
Compression=lzma
SolidCompression=yes
DisableDirPage=no
DisableProgramGroupPage=no

;-----------------------------
; الملفات اللي ينسخها الـ Setup
;-----------------------------
[Files]
; ملف البرنامج النهائي اللي طلع من PyInstaller
Source: "D:\my app\orphans_app\dist\OrphansApp.exe"; DestDir: "{app}"; Flags: ignoreversion

; 🚫 لا تنسخ قاعدة البيانات إلى Program Files
; البرنامج هسه يستعمل قاعدة بيانات داخل %APPDATA%\OrphansApp
; وخليها هو ينشئها أول مرة يشغل.
;Source: "D:\my app\orphans_app\orphans.db"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; ملف إعدادات البرنامج (إذا موجود بجانب السكربت)
Source: "{#SourcePath}\app_settings.ini"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

;-----------------------------
; الاختصارات
;-----------------------------
[Icons]
; اختصار في قائمة Start
Name: "{group}\نظام كفالة الأيتام"; Filename: "{app}\OrphansApp.exe"

; اختصار على سطح المكتب
Name: "{commondesktop}\نظام كفالة الأيتام"; Filename: "{app}\OrphansApp.exe"; Tasks: desktopicon

;-----------------------------
; خيارات إضافية (اختصار سطح المكتب)
;-----------------------------
[Tasks]
Name: "desktopicon"; Description: "إنشاء اختصار على سطح المكتب"; GroupDescription: "خيارات إضافية:"
