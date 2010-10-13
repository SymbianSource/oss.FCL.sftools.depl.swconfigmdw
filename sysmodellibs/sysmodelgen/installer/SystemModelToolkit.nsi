
; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "SystemModelToolkit"
!define PRODUCT_VERSION "1.1.9"
!define PRODUCT_PUBLISHER "Symbian Software Ltd"
!define PRODUCT_WEB_SITE "http://www.symbian.com"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install-full.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall-full.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of SystemModelToolkit 1.1\n\nClick Next to continue..."
!insertmacro MUI_PAGE_WELCOME
; License page
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE "license.txt"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "SystemModelToolkitInstaller.exe"
InstallDir "D:\SystemModelToolkit"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show


;--------------------------- INSTALL SECTION ---------------------------
Section "Install Files" SEC01

  SetOutPath "$INSTDIR"
  SetOverwrite try
  File "..\src\old\svg\DrawSvg.pl"

  SetOutPath "$INSTDIR\src\old\svg"
  SetOverwrite try
  File "..\src\old\svg\Draw.xsl"
  File "..\src\old\svg\DrawSvg.pl"
  File "..\src\old\svg\DrawSvg.pm"
  File "..\src\old\svg\Legend.xsl"
  File "..\src\old\svg\Model.xsl"
  File "..\src\old\svg\ModelTemplate.mid.xml"
  File "..\src\old\svg\ModelTemplate.older.xml"
  File "..\src\old\svg\ModelTemplate.xml"
  File "..\src\old\svg\output-csv.xsl"
  File "..\src\old\svg\output-sysdef.xsl"
  File "..\src\old\svg\Overlay.xsl"
  File "..\src\old\svg\Postprocess.xsl"
  File "..\src\old\svg\Shapes.xsl"
  File "..\src\old\svg\sysdefdowngrade.xsl"
  File "..\src\old\svg\validate-raw.xsl"
  File "..\src\old\svg\validate.xsl"

  SetOutPath "$INSTDIR\src\old\resources\auxiliary"
  SetOverwrite try
  File "..\src\old\resources\auxiliary\display-names.xml"
  File "..\src\old\resources\auxiliary\Example-shapes.xml"
  File "..\src\old\resources\auxiliary\Levels.xml"
  File "..\src\old\resources\auxiliary\Levels91.xml"
  File "..\src\old\resources\auxiliary\Shapes.xml"
  File "..\src\old\resources\auxiliary\system_model_colors.xml"
  File "..\src\old\resources\auxiliary\SystemInfo.xml"


  SetOutPath "$INSTDIR\src\old\resources\xsd"
  SetOverwrite try
  File "..\src\old\resources\xsd\Border-shapes.xsd"
  File "..\src\old\resources\xsd\Border-styles.xsd"
  File "..\src\old\resources\xsd\Colours.xsd"
  File "..\src\old\resources\xsd\Levels.xsd"
  File "..\src\old\resources\xsd\Localisation.xsd"
  File "..\src\old\resources\xsd\Patterns.xsd"
  File "..\src\old\resources\xsd\Shapes.xsd"

  
  SetOutPath "$INSTDIR\src"
  SetOverwrite try
  File "..\src\Logger.pm"
  File "..\src\LogItem.pm"

  SetOutPath "$INSTDIR\rsc\installed\Xalan"
  SetOverwrite try
  File "..\rsc\installed\Xalan\Xalan-C_1_8.dll"
  File "..\rsc\installed\Xalan\Xalan.exe"
  File "..\rsc\installed\Xalan\XalanMessages_1_8.dll"
  File "..\rsc\installed\Xalan\xerces-c_2_5_0.dll"

  SetOutPath "$INSTDIR\resources\auxiliary"
  SetOverwrite try
  File "..\resources\auxiliary\system_model_colors.xml"
  File "..\resources\auxiliary\display-names.xml"
  File "..\resources\auxiliary\Levels.xml"
  File "..\resources\auxiliary\Levels91.xml"
  File "..\resources\auxiliary\Shapes.xml"
  File "..\resources\auxiliary\Example-shapes.xml"
  File "..\resources\auxiliary\SystemInfo.xml"



SectionEnd
;-------------------------------------------------------


Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd


;--------------------------- UNISTALL SECTION ---------------------------
Section Uninstall

  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\rsc\installed\Xalan\Xalan-C_1_8.dll"
  Delete "$INSTDIR\rsc\installed\Xalan\Xalan.exe"
  Delete "$INSTDIR\rsc\installed\Xalan\XalanMessages_1_8.dll"
  Delete "$INSTDIR\rsc\installed\Xalan\xerces-c_2_5_0.dll"
  Delete "$INSTDIR\src\old\resources\auxiliary\display-names.xml"
  Delete "$INSTDIR\src\old\resources\auxiliary\Example-shapes.xml"
  Delete "$INSTDIR\src\old\resources\auxiliary\Levels.xml"
  Delete "$INSTDIR\src\old\resources\auxiliary\Levels91.xml"
  Delete "$INSTDIR\src\old\resources\auxiliary\Shapes.xml"
  Delete "$INSTDIR\src\old\resources\auxiliary\system_model_colors.xml"
  Delete "$INSTDIR\src\old\resources\auxiliary\SystemInfo.xml"
  Delete "$INSTDIR\src\old\resources\xsd\Border-shapes.xsd"
  Delete "$INSTDIR\src\old\resources\xsd\Border-styles.xsd"
  Delete "$INSTDIR\src\old\resources\xsd\Colours.xsd"
  Delete "$INSTDIR\src\old\resources\xsd\Levels.xsd"
  Delete "$INSTDIR\src\old\resources\xsd\Localisation.xsd"
  Delete "$INSTDIR\src\old\resources\xsd\Patterns.xsd"
  Delete "$INSTDIR\src\old\resources\xsd\Shapes.xsd"
  Delete "$INSTDIR\src\old\svg\Draw.xsl"
  Delete "$INSTDIR\src\old\svg\DrawSvg.pl"
  Delete "$INSTDIR\src\old\svg\DrawSvg.pm"
  Delete "$INSTDIR\src\old\svg\Legend.xsl"
  Delete "$INSTDIR\src\old\svg\Model.xsl"
  Delete "$INSTDIR\src\old\svg\ModelTemplate.mid.xml"
  Delete "$INSTDIR\src\old\svg\ModelTemplate.older.xml"
  Delete "$INSTDIR\src\old\svg\ModelTemplate.xml"
  Delete "$INSTDIR\src\old\svg\output-csv.xsl"
  Delete "$INSTDIR\src\old\svg\output-sysdef.xsl"
  Delete "$INSTDIR\src\old\svg\Overlay.xsl"
  Delete "$INSTDIR\src\old\svg\Postprocess.xsl"
  Delete "$INSTDIR\src\old\svg\Shapes.xsl"
  Delete "$INSTDIR\src\old\svg\sysdefdowngrade.xsl"
  Delete "$INSTDIR\src\Logger.pm"
  Delete "$INSTDIR\src\LogItem.pm"

  RMDir "$INSTDIR\src\old\svg"
  RMDir "$INSTDIR\common"
  RMDir "$INSTDIR\src\old\resources\auxiliary"
  RMDir "$INSTDIR\src\old\resources"
  RMDir "$INSTDIR\rsc"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd
;-------------------------------------------------------


