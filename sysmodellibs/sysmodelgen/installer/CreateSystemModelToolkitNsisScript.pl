# Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description:
#

my $installScript = $ARGV[0] ? $ARGV[0] : "my_systemmodeltoolkit.nsi";

my $productName = "SystemModelToolkit";
my $productVersion = "1.1";

my $depDir = ".."; # The location of Dep directory

# all directory pathnames are relative to DepToolkit\Dep
my @subDirsToInstall = ("src\\svg");
my %individualFilesToInstall = ();

my @filesToUnistall = (); # w.r.t the root of installation directory
my @dirsToUnistall = (); # w.r.t the root of installation directory

CreateInstallScript();

sub CreateInstallScript()
	{
	open (SCRIPT, ">$installScript") or die "Cannot open $installScript to write to: $!";
	print SCRIPT Header();
	print SCRIPT InstallationTextSection();
	print SCRIPT Middle();
	print SCRIPT UninstallationTextSection();
	}

sub InstallationTextSection()
	{
	my $text = "\n;--------------------------- INSTALL SECTION ---------------------------\nSection \"Install Files\" SEC01\n\n";
	
	my $directory = "src\\svg";
	
	# Copy the main script, DrawSvg.pl into the root of installtion directory:
	$text .= "  SetOutPath \"\$INSTDIR\"\n";
	$text .= "  SetOverwrite try\n";
	$text .= "  File \"$depDir\\$directory\\DrawSvg.pl\"\n";
	push @filesToUnistall, "DrawSvg.pl";
	$text .= "  File \"$depDir\\$directory\\distribution.policy\"\n";
	push @filesToUnistall, "distribution.policy";
	$text .= "\n";
	
	# rest of the svg files' in SVG
	$text .= "  SetOutPath \"\$INSTDIR\\svg\"\n";
	$text .= "  SetOverwrite try\n";
	opendir DIR, "$depDir\\$directory" or die "Directory $depDir\\$directory doesn't exist...\n";
	my @files = readdir DIR;
	closedir DIR;
	foreach my $file (@files)
		{
		#next if $file =~ m/^\.+$/;
		#next if -d $file; # no sub-directories need installing
		#next if lc $file eq "drawsvg.pl"; # .pl script goes in the root of installation (covered above).
		
		# only install the .pm, .xsl, .xml, .ini and .policy files
		next if lc $file !~ m/\.xsl$/ and 
				 lc $file !~ m/\.xml$/ and 
				 lc $file !~ m/\.pm$/ and 
				 lc $file !~ m/\.ini$/ and 
				 lc $file !~ m/\.policy$/; 
		
		$text .= "  File \"$depDir\\$directory\\$file\"\n";
		push @filesToUnistall, "svg\\$file";
		}
	$text .= "\n";
	push @dirsToUnistall, "svg";
	
	# now copy the common files:
	$directory = "src\\common";
	$text .= "  SetOutPath \"\$INSTDIR\\common\"\n";
	$text .= "  SetOverwrite try\n";
	@files = ("DepConstants.pm", "Logger.pm", "LogItem.pm", "distribution.policy");
	foreach my $file (@files)
		{
		$text .= "  File \"$depDir\\$directory\\$file\"\n";
		push @filesToUnistall, "common\\$file";
		}
	$text .= "\n";
	push @dirsToUnistall, "common";
	
	$directory = "resources\\installed\\Xalan";
	$text .= "  SetOutPath \"\$INSTDIR\\resources\\installed\\Xalan\"\n";
	$text .= "  SetOverwrite try\n";
	opendir DIR, "$depDir\\$directory" or die "Directory $depDir\\$directory doesn't exist...\n";
	my @files = readdir DIR;
	closedir DIR;
	foreach my $file (@files)
		{
		next if $file =~ m/^\.+$/;
		next if -d $file; # no sub-directories need installing
		$text .= "  File \"$depDir\\$directory\\$file\"\n";
		push @filesToUnistall, "$directory\\$file";
		}
	$text .= "\n";
	
	# now copy the common files:
	$directory = "resources\\auxiliary";
	$text .= "  SetOutPath \"\$INSTDIR\\resources\\auxiliary\"\n";
	$text .= "  SetOverwrite try\n";
	opendir DIR, "$depDir\\$directory" or die "Directory $depDir\\$directory doesn't exist...\n";
	my @files = readdir DIR;
	closedir DIR;
	foreach my $file (@files)
		{
		next if $file =~ m/^\.+$/;
		next if -d $file; # no sub-directories need installing
		$text .= "  File \"$depDir\\$directory\\$file\"\n";
		push @filesToUnistall, "$directory\\$file";
		}
	$text .= "\n";
	
	# remember all the resource directories for deletion:
	push @dirsToUnistall, "resources\\installed\\Xalan";
	push @dirsToUnistall, "resources\\installed";
	push @dirsToUnistall, "resources\\auxiliary";
	push @dirsToUnistall, "resources";
	
	# finally the documentation:
	$directory = "docs";
	$text .= "  SetOutPath \"\$INSTDIR\\docs\"\n";
	$text .= "  SetOverwrite try\n";
	@files = ("Building the System Model.doc", "distribution.policy", "dep.css", "sample_drawsvg.ini", "SystemModelToolkitInstaller_main.jpg", "user_guide_system_model_toolkit.html");
	foreach my $file (@files)
		{
		$text .= "  File \"$depDir\\$directory\\$file\"\n";
		push @filesToUnistall, "docs\\$file";
		}
	$text .= "\n";
	push @dirsToUnistall, "docs";
	
	$text .= "\nSectionEnd\n;-------------------------------------------------------\n\n";
	return $text;
	}

sub UninstallationTextSection()
	{
	my $text = "\n;--------------------------- UNISTALL SECTION ---------------------------\nSection Uninstall\n\n";
	$text .= "  Delete \"\$INSTDIR\\uninst.exe\"\n";

	foreach $file (@filesToUnistall)
		{
		$text .= "  Delete \"\$INSTDIR\\$file\"\n";
		}
	
	$text .= "\n";
	foreach $directory (@dirsToUnistall)
		{
		$text .= "  RMDir \"\$INSTDIR\\$directory\"\n";
		}
	
	$text .= <<TEXT;
  RMDir "\$INSTDIR"

  DeleteRegKey \${PRODUCT_UNINST_ROOT_KEY} "\${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd
;-------------------------------------------------------


TEXT
	return $text;
	}

sub Header()
	{
	return <<TEXT;

; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "$productName"
!define PRODUCT_VERSION "$productVersion"
!define PRODUCT_PUBLISHER "Symbian Software Ltd"
!define PRODUCT_WEB_SITE "http://www.symbian.com"
!define PRODUCT_UNINST_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "\${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-install-full.ico"
!define MUI_UNICON "\${NSISDIR}\\Contrib\\Graphics\\Icons\\modern-uninstall-full.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of $productName $productVersion\\n\\nClick Next to continue..."
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

Name "\${PRODUCT_NAME} \${PRODUCT_VERSION}"
OutFile "SystemModelToolkitInstaller.exe"
InstallDir "D:\\SystemModelToolkit"
InstallDirRegKey HKLM "\${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

TEXT
	}

sub Middle()
	{
	return <<TEXT;

Section -Post
  WriteUninstaller "\$INSTDIR\\uninst.exe"
  WriteRegStr \${PRODUCT_UNINST_ROOT_KEY} "\${PRODUCT_UNINST_KEY}" "DisplayName" "\$(^Name)"
  WriteRegStr \${PRODUCT_UNINST_ROOT_KEY} "\${PRODUCT_UNINST_KEY}" "UninstallString" "\$INSTDIR\\uninst.exe"
  WriteRegStr \${PRODUCT_UNINST_ROOT_KEY} "\${PRODUCT_UNINST_KEY}" "DisplayVersion" "\${PRODUCT_VERSION}"
  WriteRegStr \${PRODUCT_UNINST_ROOT_KEY} "\${PRODUCT_UNINST_KEY}" "URLInfoAbout" "\${PRODUCT_WEB_SITE}"
  WriteRegStr \${PRODUCT_UNINST_ROOT_KEY} "\${PRODUCT_UNINST_KEY}" "Publisher" "\${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "\$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove \$(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

TEXT
	}

exit;
