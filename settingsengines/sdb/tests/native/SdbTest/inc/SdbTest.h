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
 Name		: SdbTest.h
 Author	  : 
 Copyright   : Your copyright notice
 Description : Exe header file
 ============================================================================
 */

#ifndef __SDBTEST_H__
#define __SDBTEST_H__

//  Include Files

#include <e32base.h>
#include "SdbTestFramework.h"

// Globals

typedef int (*TTestFunction)(RSdbTest&);

//  Function Prototypes

GLDEF_C TInt E32Main();

#endif  // __SDBTEST_H__

