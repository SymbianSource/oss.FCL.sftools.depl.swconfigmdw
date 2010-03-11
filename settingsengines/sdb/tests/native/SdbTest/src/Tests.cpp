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
 * Tests.cpp
 *
 */

#include "SdbTest.h"

extern void RegisterTestL(const TDesC&, TTestFunction);


// //
// Add a test function prototype here 
int ExampleTestL(RSdbTest& aTest);

// //
// Register your test here 
//
void RegisterTestsL()
	{
	_LIT(KExampleTestName, "ExampleTest");
	RegisterTestL(KExampleTestName, &ExampleTestL);
	}


// //
// You can add 
int ExampleTestL(RSdbTest& aTest)
	{
	CCommandLineArguments* cmdLine = aTest.CommandLineArgumentsL();
	aTest.AssertTrueL(ETrue	, __LINE__);
	aTest.Next(_L("Test #1"));
	aTest.AssertNotErrorL(KErrNone, __LINE__);
	aTest.EndL(KErrNone);
	aTest.Printf(_L("You can print stuff like this %d\n"), KErrNone);
	return KErrNone;
	}


