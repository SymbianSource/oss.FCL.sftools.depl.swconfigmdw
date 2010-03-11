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
 Name		: SdbTest.cpp
 Author	  : 
 Copyright   : Your copyright notice
 Description : Exe source file
 ============================================================================
 */
#include "SdbTest.h"
#include <e32base.h>
#include <e32std.h>
#include <e32cons.h>			// Console
#include <bacline.h>


_LIT(KTextConsoleTitle, "Console");
_LIT(KTextFailed, " failed, leave code = %d");
_LIT(KTextPressAnyKey, " [press any key]\n");

RArray<const TDesC> *gTestNames;
RArray<TTestFunction> *gTestFuncs;
extern void RegisterTestsL();

//  Do your test here
LOCAL_C void MainL(RSdbTest& aTest)
	{
	CCommandLineArguments* cmdLine = aTest.CommandLineArgumentsL();
	TInt count = cmdLine->Count();  
	if ( count < 2 )
		{
		User::Leave(KErrArgument);
		}
	TInt index = KErrNotFound;
	TPtrC testName = cmdLine->Arg(1);
	for( TInt i = 0; i < gTestNames->Count(); i++ )
		{
		if ( testName.CompareF((*gTestNames)[i]) )
			{
			index = i;
			break;
			}
		}
	User::LeaveIfError(index);
	TTestFunction function = (*gTestFuncs)[index]; 
	User::LeaveIfError((*function)(aTest));
	}

void RegisterTestL(const TDesC& aTestName, TTestFunction aFunc)
	{
	gTestNames->AppendL(aTestName);
	gTestFuncs->AppendL(aFunc);
	}


LOCAL_C void DoStartL(RSdbTest& aTest)
	{
	RArray<const TDesC> nameMap;
	CleanupClosePushL(nameMap);
	RArray<TTestFunction> funcMap;
	CleanupClosePushL(funcMap);
	gTestNames = &nameMap;
	gTestFuncs = &funcMap;
	RegisterTestsL();
	MainL(aTest);
	CleanupStack::PopAndDestroy(2);
	}

//  Global Functions

GLDEF_C TInt E32Main()
	{
	// Create cleanup stack
	__UHEAP_MARK;
	CTrapCleanup* cleanup = CTrapCleanup::New();
	TInt error = KErrNone;
	
	CConsoleBase* console = NULL;
	TRAP(error, console = Console::NewL(KTextConsoleTitle, TSize(
			KConsFullScreen, KConsFullScreen)));
	if (error)
		return error;

	RSdbTest test;
	test.SetConsole(console);
	test.SetLogged(ETrue);
	TRAP(error, test.StartL(_L("Test start")));
	if (error)
		return error;

	// Run application code inside TRAP harness, wait keypress when terminated
	TRAP(error, DoStartL(test));
	if (error)
		console->Printf(KTextFailed, error);
	console->Printf(KTextPressAnyKey);
	test.Getch();
	TRAPD(err, test.CloseL());

	delete cleanup;
	__UHEAP_MARKEND;
	return error;
	}

