#!perl
# Copyright (c) 2004-2009 Nokia Corporation and/or its subsidiary(-ies).
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

package DepConstants;

use FindBin;
use lib $FindBin::Bin;
use strict;
use Cwd;

# -------------------------------------------------------
# 	Data stores, etc
# -------------------------------------------------------
my $KDataDirectory = $FindBin::Bin."deptoolkit_data";
sub DataDirectory     { return $KDataDirectory; }

my $KDataFile = $FindBin::Bin."deptoolkit_data"; # this is the default value, to be used if the user hasn't specified a value
sub DataFile     { return $KDataFile; }

# -------------------------------------------------------
# 	Html and icons files:
# -------------------------------------------------------
my $KIconsSourceDirectory = $FindBin::Bin."/../resources/html/icons";
sub IconsSource() { return $KIconsSourceDirectory; }

my $KZoomInIcon = "dep_zoom_in.gif";
my $KZoomInDisabledIcon = "dep_zoom_in_disabled.gif";
my $KTopOfPageIcon = "dep_top_of_page.gif";
my $KSeperatorIcon = "dep_separator.gif";
my $KArrowIcon = "dep_arrow.gif";
my $KAtSignIcon = "dep_at_sign.gif";
my $KHierarchyIcon = "dep_hierarchy.gif";
my $KSysDefIcon = "dep_sysdef.gif";
my $KLayerIcon = "dep_layer.gif";
my $KBlockIcon = "dep_block.gif";
my $KSubBlockIcon = "dep_sub_block.gif";
my $KCollectionIcon = "dep_collection.gif";
my $KComponentIcon = "dep_component.gif";
my $KExeIcon = "dep_exe.gif";
my $KWarningIcon = "dep_warning.gif";

sub ZoomInIcon() { return $KZoomInIcon; }
sub ZoomInDisabledIcon() { return $KZoomInDisabledIcon; }
sub TopOfPageIcon() { return $KTopOfPageIcon; }
sub SeperatorIcon() { return $KSeperatorIcon; }
sub ArrowIcon() { return $KArrowIcon; }
sub AtSignIcon() { return $KAtSignIcon; }
sub HierarchyIcon() { return $KHierarchyIcon; }
sub SysDefIcon() { return $KSysDefIcon; }
sub LayerIcon() { return $KLayerIcon; }
sub BlockIcon() { return $KBlockIcon; }
sub SubBlockIcon() { return $KSubBlockIcon; }
sub CollectionIcon() { return $KCollectionIcon; }
sub ComponentIcon() { return $KComponentIcon; }
sub ExeIcon() { return $KExeIcon; }
sub WarningIcon() {return $KWarningIcon; }

# Following methods contsruct the HTML image tags using the source directory
# (For output files, use the ImgHtml() by passing the /icons directory file names)
sub ZoomInImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KZoomInIcon", 'Causal details of relationship');
	}

sub ZoomInDisabledImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KZoomInDisabledIcon", 'Manual dependency: no details available');
	}

sub TopOfPageImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KTopOfPageIcon", 'Top', "\#_top");
	}

sub SeperatorImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KSeperatorIcon");
	}

sub ArrowImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KArrowIcon");
	}

sub AtSignImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KAtSignIcon", 'is located at');
	}

sub HierarchyImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KHierarchyIcon", "System Model Hierarchy");
	}

sub SysDefImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KSysDefIcon");
	}

sub LayerImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KLayerIcon", "Layer");
	}

sub BlockImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KBlockIcon", "Block");
	}

sub SubBlockImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KSubBlockIcon", "Sub-block");
	}

sub CollectionImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KCollectionIcon", "Collection");
	}

sub ComponentImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KComponentIcon", "Component");
	}

sub ExeImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KExeIcon", "Executable");
	}

sub WarningImgHtml()
	{
	my $hrefRelativeDepth = $_[0] ? $_[0] : 0;
	return RelativeImgHtml($hrefRelativeDepth, "icons/$KWarningIcon", "Warning");
	}

# Genric:
sub RelativeImgHtml()
	{
	my $hrefRelativeDepth = shift;
	my $img = shift; # image file
	my $alt = shift; # tool tip text
	my $url = shift; # if a url is given, turn it into a href
	
    my $relativeDirText = ""; # where the main index file is.
	$relativeDirText = "../" x $hrefRelativeDepth if defined $hrefRelativeDepth;
    $relativeDirText =~ s@\/$@@; # now remove the trailing slash
    $img = $relativeDirText."/".$img;
    
    return ImgHtml($img, $alt, $url);
	}

sub ImgHtml()
	{
	my $img = shift; # image file
	my $alt = shift; # tool tip text
	my $url = shift; # if a url is given, turn it into a href
	my $imgHtml = "";
	return $imgHtml if $img eq "";
	$imgHtml .= "<a href='$url'>" if $url;
	$imgHtml .= "<img src='$img'";
	$imgHtml .= " alt='$alt'" if $alt; # optional
	$imgHtml .= " border = '0'>";
	$imgHtml .= "</a>" if $url;
	return $imgHtml;
	}


# -------------------------------------------------------
# 	Homepage and other files:
# -------------------------------------------------------
my $KHtmlSourceDirectory = $FindBin::Bin."/../resources/html";
sub HtmlSourceDirectory() { return $KHtmlSourceDirectory; }

my $KHomepageFileName = "index.html";
my $KHomepage = $KHtmlSourceDirectory."/".$KHomepageFileName;
sub HomepageFileName() { return $KHomepageFileName; }
sub Homepage() { return $KHomepage; }

my $KSysModelHtmlName = "sysmodel.html";
sub SysModelHtmlName() { return $KSysModelHtmlName; }

my @KAuxiliaryHtmlFiles = ("metrics.html", "model_criteria.html",  "user_guide.html", "coupling.pdf");
sub AuxiliaryHtmlFiles() { return @KAuxiliaryHtmlFiles; }

my $KCssStylesheetFileName = "dep.css";
my $KCssStylesheet = $FindBin::Bin."/../resources/html/css/".$KCssStylesheetFileName;
sub CssStylesheetFileName() { return $KCssStylesheetFileName; }
sub CssStylesheet() { return $KCssStylesheet; }

my $KInstallerImageFileName = "DepToolkitInstaller_main.jpg";
my $KInstallerImage = $FindBin::Bin."/../resources/html/images/DepToolkitInstaller_main.jpg";
sub InstallerImageFileName() { return $KInstallerImage; }
sub InstallerImage() { return $KInstallerImage; }

my $KCustomisationJavaScript = "custom.js";
sub CustomisationJavaScript() { return $KCustomisationJavaScript; }

# -------------------------------------------------------
#	Misc constants:
# -------------------------------------------------------
# Relationship type between two items:
use constant KDependency						=> 1;
use constant KDependent							=> 2;
# Dependency type between two items:
use constant KStaticDependency					=> 1;
use constant KDynamicDependency					=> 2;
use constant KManualDependency					=> 3;

# -------------------------------------------------------
# 	ERROR & WARNING CODES
# -------------------------------------------------------

use constant KErrorNone							=> 0;

use constant KIncorrectSyntax					=> 1;
use constant KFileDoesNotExist					=> 2;
use constant KCannotOpenFile					=> 3;
use constant KInvalidROMLog						=> 4;
use constant KBinaryNotInROM					=> 5;
use constant KNoBinariesInROM					=> 6;
use constant KBinaryDoesNotExist				=> 7;
use constant KMapFileDoesNotExist				=> 8;
use constant KFailure							=> 9;

# System_Definition.xml error codes:
use constant KSysDefNotFound					=> 31;
use constant KInvalidSysDefXML					=> 32;
use constant KConfigurationNotFound				=> 33;

# Graphing error codes:
use constant KDotExeNotFound					=> 41;

# HTML rendering error codes:
#

# Codes for scripts and modules (starting at 100):
use constant KStartOfScriptCodes				=> 100;
use constant KUnknownModule						=> 100;
use constant KModel								=> 101;
use constant KFileMaps							=> 102;
use constant KDepInfo							=> 103;
use constant KDepInfoToLinkDeps					=> 104;
use constant KDepInfoToHtml						=> 105;
use constant KDepsTree							=> 106;
use constant KModelEngine						=> 107;
use constant KDepRendererCommon					=> 108;
use constant KDepSummariesRenderer				=> 109;
use constant KDepDetailsRenderer				=> 110;
use constant KGenGraphs							=> 111;
use constant KSysDefParser						=> 112;
use constant KSysModelDepsGenerator				=> 113;
use constant KDepsCommon						=> 114;
use constant KDotDigraph						=> 115;

# Logging severity levels:
use constant ERROR 								=> 1;
use constant WARNING							=> 2;
use constant INFO 								=> 3;
use constant VERBOSE							=> 4;

# Script or module-level error codes (starting at 200):
use constant KUnknownModuleError				=> 200;
use constant KModelError						=> 201;
use constant KFileMapsError						=> 202;
use constant KDepInfoError						=> 203;
use constant KDepInfoToLinkDepsError			=> 204;
use constant KDepInfoToHtmlError				=> 205;
use constant KDepsTreeError						=> 206;
use constant KModelEngineError					=> 207;
use constant KDepRendererCommonError			=> 208;
use constant KDepSummariesRendererError			=> 209;
use constant KDepDetailsRendererError			=> 210;
use constant KGenGraphsError					=> 211;
use constant KSysDefParserError					=> 212;
use constant KSysModelDepsGeneratorError		=> 213;
use constant KDepsCommonError					=> 214;
use constant KDotDigraphError					=> 215;

# Script or module-level warning codes (starting at 300):
use constant KUnknownModuleWarning				=> 300;
use constant KModelWarning						=> 301;
use constant KFileMapsWarning					=> 302;
use constant KDepInfoWarning					=> 303;
use constant KDepInfoToLinkDepsWarning			=> 304;
use constant KDepInfoToHtmlWarning				=> 305;
use constant KDepsTreeWarning					=> 306;
use constant KModelEngineWarning				=> 307;
use constant KDepRendererCommonWarning			=> 308;
use constant KDepSummariesRendererWarning		=> 309;
use constant KDepDetailsRendererWarning			=> 310;
use constant KGenGraphsWarning					=> 311;
use constant KSysDefParserWarning				=> 312;
use constant KSysModelDepsGeneratorWarning		=> 313;
use constant KDepsCommonWarning					=> 314;
use constant KDotDigraphWarning					=> 315;

# Script or module-level info codes (starting at 400):
use constant KUnknownModuleInfo					=> 400;
use constant KModelInfo							=> 401;
use constant KFileMapsInfo						=> 402;
use constant KDepInfoInfo						=> 403;
use constant KDepInfoToLinkDepsInfo				=> 404;
use constant KDepInfoToHtmlInfo					=> 405;
use constant KDepsTreeInfo						=> 406;
use constant KModelEngineInfo					=> 407;
use constant KDepRendererCommonInfo				=> 408;
use constant KDepSummariesRendererInfo			=> 409;
use constant KDepDetailsRendererInfo			=> 410;
use constant KGenGraphsInfo						=> 411;
use constant KSysDefParserInfo					=> 412;
use constant KSysModelDepsGeneratorInfo			=> 413;
use constant KDepsCommonInfo					=> 414;
use constant KDotDigraphInfo					=> 415;

my @KUnknownModuleCodes       		= (KUnknownModuleError, KUnknownModuleWarning, KUnknownModuleInfo);
my @KModelCodes       				= (KModelError, KModelWarning, KModelInfo);
my @KFileMapsCodes 					= (KFileMapsError, KFileMapsWarning, KFileMapsInfo);
my @KDepInfoCodes 					= (KDepInfoError, KDepInfoWarning, KDepInfoInfo);
my @KDepInfoToHtmlCodes 		 	= (KDepInfoToHtmlError, KDepInfoToHtmlWarning, KDepInfoToHtmlInfo);
my @KDepInfoToLinkDepsCodes 		= (KDepInfoToLinkDepsError, KDepInfoToLinkDepsWarning, KDepInfoToLinkDepsInfo);
my @KDepsTreeCodes       			= (KDepsTreeError, KDepsTreeWarning, KDepsTreeInfo);
my @KModelEngineCodes				= (KModelEngineError, KModelEngineWarning, KModelEngineInfo);
my @KDepRendererCommonCodes			= (KDepRendererCommonError, KDepRendererCommonWarning, KDepRendererCommonInfo);
my @KDepSummariesRendererCodes     	= (KDepSummariesRendererError, KDepSummariesRendererWarning, KDepSummariesRendererInfo);
my @KDepDetailsRendererCodes       	= (KDepDetailsRendererError, KDepDetailsRendererWarning, KDepDetailsRendererInfo);
my @KGenGraphsCodes       			= (KGenGraphsError, KGenGraphsWarning, KGenGraphsInfo);
my @KSysDefParserCodes       		= (KSysDefParserError, KSysDefParserWarning, KSysDefParserInfo);
my @KSysModelDepsGeneratorCodes   	= (KSysModelDepsGeneratorError, KSysModelDepsGeneratorWarning, KSysModelDepsGeneratorInfo);
my @KDepsCommonCodes   				= (KDepsCommonError, KDepsCommonWarning, KDepsCommonInfo);
my @KDotDigraphCodes   				= (KDotDigraphError, KDotDigraphWarning, KDotDigraphInfo);

sub ModuleErrorCodes()
	{
	my $moduleCode = shift;
	--(my $level = shift); # decrement as it's an index into an array
	return 0 if $moduleCode < KStartOfScriptCodes or $level < 0 or $level > 2;
	return $KModelCodes[$level] 				if ($moduleCode == KModel);
	return $KFileMapsCodes[$level] 				if ($moduleCode == KFileMaps);
	return $KDepInfoCodes[$level] 				if ($moduleCode == KDepInfo);
	return $KDepInfoToLinkDepsCodes[$level]		if ($moduleCode == KDepInfoToLinkDeps);
	return $KDepInfoToHtmlCodes[$level] 		if ($moduleCode == KDepInfoToHtml);
	return $KDepsTreeCodes[$level] 				if ($moduleCode == KDepsTree);
	return $KModelEngineCodes[$level] 			if ($moduleCode == KModelEngine);
	return $KDepRendererCommonCodes[$level] 	if ($moduleCode == KDepRendererCommon);
	return $KDepSummariesRendererCodes[$level] 	if ($moduleCode == KDepSummariesRenderer);
	return $KDepDetailsRendererCodes[$level] 	if ($moduleCode == KDepDetailsRenderer);
	return $KGenGraphsCodes[$level] 			if ($moduleCode == KGenGraphs);
	return $KSysDefParserCodes[$level] 			if ($moduleCode == KSysDefParser);
	return $KSysModelDepsGeneratorCodes[$level] if ($moduleCode == KSysModelDepsGenerator);
	return $KDepsCommonCodes[$level]			if ($moduleCode == KDepsCommon);
	return $KDotDigraphCodes[$level]			if ($moduleCode == KDotDigraph);
	
	return $KUnknownModuleCodes[$level];
	}

#-----------------------------------------------------------------------------
# EPOCROOT, NM, CPPFILT, PETRAN
#-----------------------------------------------------------------------------
my $EPOCROOT = $ENV{EPOCROOT};

# Global Variables:
my $NM          = "nm.exe";
my $CPPFILT     = "c++filt.exe";
my $PETRAN      = "petran.exe";
my $ELFTRAN     = "elftran.exe";

sub EPOCROOT    { return $EPOCROOT; } 
sub NM          { return $NM; }
sub CPPFILT     { return $CPPFILT; }
sub PETRAN      { return $PETRAN; }
sub ELFTRAN     { return $ELFTRAN; }

#-----------------------------------------------------------------------------
# DOT (Graphing tool)
#-----------------------------------------------------------------------------
my $KDOTDirectory = $FindBin::Bin."/../resources/installed/Dot";
my $KDOT = $KDOTDirectory."/dot.exe -q";
sub Dot     	{ return $KDOT." -q1"; }

my $KNEATO = $KDOTDirectory."/neato.exe";
sub Neato     	{ return $KNEATO; }

# -------------------------------------------------------
# 	Auxiliary files:
# -------------------------------------------------------
my $KAuxiliaryDirectory = $FindBin::Bin."/resources/auxiliary";
my $KSystemModelColorsXmlFile = $KAuxiliaryDirectory."/system_model_colors.xml";
my $KSystemModelExtraInfoXmlFile = $KAuxiliaryDirectory."/SystemInfo.xml";

sub SystemModelColorsXmlFile()
	{
	my $colorsFile = $KSystemModelColorsXmlFile;
	$colorsFile = $FindBin::Bin."/../../resources/auxiliary/system_model_colors.xml" if ! -e $colorsFile;
	return $colorsFile;
	}

sub SystemModelXmlDataDir()
	{
	my $file = $KAuxiliaryDirectory;
	$file = $FindBin::Bin."/../../resources/auxiliary" if ! -e $file;
	return $file;
	}

#-----------------------------------------------------------------------------
# Xalan
#-----------------------------------------------------------------------------
my $KXalanDirectory = $FindBin::Bin."/resources/installed/Xalan";
my $KXalan = $KXalanDirectory."/xalan.exe";
sub Xalan()
	{
	my $xalan = $KXalan;
	$xalan = $FindBin::Bin."/../../resources/installed/Xalan/xalan.exe" if ! -e $xalan;
	return $xalan;
	}

my $KSystemoModelSVG = $FindBin::Bin."/../temp/sysmodel.svg";
sub SystemoModelSVG { return $KSystemoModelSVG; }

#-----------------------------------------------------------------------------
# Gzip
#-----------------------------------------------------------------------------
sub GzipCommand
	{ # returns empty if gzip not in path
	foreach my $dir (split(/;/,$ENV{'PATH'}))
		{
		$dir.="\\gzip.exe";
		if(-e $dir) {return "gzip -9"}
		}
	return "";
	}


#-----------------------------------------------------------------------------
# Logging
#-----------------------------------------------------------------------------
my $KLogDirectory = $FindBin::Bin."/../temp";
my $KDepToolkitLogFile = $KLogDirectory."/log.txt";
sub LogFile { return $KDepToolkitLogFile; }

1;
