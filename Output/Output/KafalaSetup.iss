;-----------------------------
; إعدادات البرنامج الأساسية
;-----------------------------
[Setup]
AppName=نظام الكفالة والرعاية المتكامل
AppVersion=1.0
AppPublisher=Hamza Altaie
DefaultDirName={autopf}\SmartKafala
DefaultGroupName=نظام الكفالة والرعاية المتكامل
OutputBaseFilename=SmartKafala_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
WizardStyle=modern
DisableDirPage=no

; 1. إضافة أيقونة لملف التنصيب (Setup)
; تأكد أن لديك ملف أيقونة بامتداد .ico في مسار المشروع
SetupIconFile=D:\my app\orphans_app\logo.ico

; (اختياري) لإضافة صورة جانبية وصورة صغيرة داخل نافذة التثبيت
; WizardImageFile=D:\my app\orphans_app\side_image.bmp
; WizardSmallImageFile=D:\my app\orphans_app\small_logo.bmp

;-----------------------------
; دعم اللغة العربية
;-----------------------------
[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

;-----------------------------
; ملفات البرنامج
;-----------------------------
[Files]
; ملف البرنامج التنفيذي
Source: "D:\my app\orphans_app\dist\OrphansApp.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. نسخ ملف الأيقونة إلى مجلد التثبيت (مهم جداً لظهور الأيقونة في الاختصارات)
Source: "D:\my app\orphans_app\logo.ico"; DestDir: "{app}"; Flags: ignoreversion

Source: "D:\my app\orphans_app\logo.png"; DestDir: "{app}"; Flags: ignoreversion

; ملف الإعدادات
Source: "D:\my app\orphans_app\app_settings.ini"; DestDir: "{commonappdata}\SponsorshipSystem"; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall; Permissions: users-modify

;-----------------------------
; الأيقونات والاختصارات
;-----------------------------
[Icons]
; 3. ربط الاختصارات بملف الأيقونة
; لاحظ إضافة IconFilename في السطرين التاليين

; اختصار قائمة ابدأ
Name: "{group}\نظام الكفالة والرعاية المتكامل"; Filename: "{app}\OrphansApp.exe"; IconFilename: "{app}\logo.ico"
; خيار حذف البرنامج
Name: "{group}\حذف النظام"; Filename: "{uninstallexe}"

; اختصار سطح المكتب
Name: "{commondesktop}\نظام الكفالة والرعاية المتكامل"; Filename: "{app}\OrphansApp.exe"; Tasks: desktopicon; IconFilename: "{app}\logo.ico"

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

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  // لا نحتاج لكود إضافي هنا حالياً
end;