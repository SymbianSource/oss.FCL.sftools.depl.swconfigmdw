// Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
// All rights reserved.
// This component and the accompanying materials are made available
// under the terms of "Eclipse Public License v1.0"
// which accompanies this distribution, and is available
// at the URL "http://www.eclipse.org/legal/epl-v10.html".
//
// Initial Contributors:
// Nokia Corporation - initial contribution.
//
// Contributors:
//
// Description:
//

/*
 ============================================================================
 Name		: SPDTestConst.h
 Author	  : 
 Copyright   : Your copyright notice
 Description : Exe header file
 ============================================================================
 */

#ifndef __SPDTESTCONST_H__
#define __SPDTESTCONST_H__

/** command line options */
_LIT(KComa,				",");
_LIT(KSpace,			" ");
_LIT(KCmdIndicator,		"-");
_LIT(KCmdVerbose, 		"v");
_LIT(KCmdMode, 			"m");
_LIT(KCmdNoWait, 		"w");

/** commandline arguments */
_LIT(KModeCreate,		"create");
_LIT(KModeValidate,		"validate");

enum TCommandId 
	{
	EInvalid 		=-1,
	ECreateIni 		= 0,
	EValidateIni 	= 1
	};

enum TCommandError
	{
	ESuccess		= 0,
	EInvalidMode 	= 1,
	EInvalidCmdArgs	= 2,
	ECntModelError 	= 3,
	EEmptyDatabase	= 4,
	EInvalideCntId	= 5
	};



#endif
