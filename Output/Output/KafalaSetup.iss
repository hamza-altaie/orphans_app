;-----------------------------
; إعدادات البرنامج الأساسية
;-----------------------------
[Setup]
; --- الاسم الجديد للنظام ---
AppName=نظام الكفالة والرعاية المتكامل
AppVersion=1.0
AppPublisher=Black Marlin
; المجلد الافتراضي للتثبيت
DefaultDirName={autopf}\SponsorshipSystem
; اسم المجلد في قائمة ابدأ
DefaultGroupName=نظام الكفالة والرعاية المتكامل
; اسم ملف التثبيت الذي سينتج (يفضل بالإنجليزية لتجنب مشاكل التحميل)
OutputBaseFilename=SponsorshipSystemSetup
Compression=lzma2
SolidCompression=yes
; طلب صلاحيات المسؤول (مهم للكتابة في Program Files)
PrivilegesRequired=admin
WizardStyle=modern
DisableDirPage=no

;-----------------------------
; دعم اللغة العربية
;-----------------------------
[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

;-----------------------------
; ملفات البرنامج
;-----------------------------
[Files]
; 1. ملف البرنامج التنفيذي (من مسارك الحالي)
Source: "D:\my app\orphans_app\dist\OrphansApp.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. ملف الإعدادات (ينسخ إلى AppData لضمان إمكانية التعديل عليه)
Source: "{#SourcePath}\app_settings.ini"; DestDir: "{userappdata}\SponsorshipSystem"; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall

; 3. (اختياري) إذا كنت تستخدم مجلد _internal
; Source: "D:\my app\orphans_app\dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

;-----------------------------
; الأيقونات والاختصارات
;-----------------------------
[Icons]
; اختصار قائمة ابدأ بالاسم الجديد
Name: "{group}\نظام الكفالة والرعاية المتكامل"; Filename: "{app}\OrphansApp.exe"
; خيار حذف البرنامج
Name: "{group}\حذف النظام"; Filename: "{uninstallexe}"

; اختصار سطح المكتب بالاسم الجديد
Name: "{commondesktop}\نظام الكفالة والرعاية المتكامل"; Filename: "{app}\OrphansApp.exe"; Tasks: desktopicon

;-----------------------------
; مهام إضافية
;-----------------------------
[Tasks]
Name: "desktopicon"; Description: "إنشاء اختصار على سطح المكتب"; GroupDescription: "خيارات إضافية:"

;-----------------------------
; التشغيل بعد التثبيت
;-----------------------------
[Run]
Filename: "{app}\OrphansApp.exe"; Description: "تشغيل النظام الآن"; Flags: nowait postinstall skipifsilent

;-----------------------------
; كود لضمان المسارات (تلقائي)
;-----------------------------
[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  // لا نحتاج لكود إضافي هنا حالياً
end;