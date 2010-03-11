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
 Name		: SpeedDialTest.cpp
 Author	  : 
 Copyright   : Your copyright notice
 Description : Exe source file
 ============================================================================
 */

//  Include Files  

#include "CenrepTest.h"
#include <e32base.h>
#include <e32std.h>
#include <e32cons.h>			// Console
#include <f32file.h>			// file i/o
#include <centralrepository.h>
#include "CommandHandler.h"
#include "cenreptestconst.h"


//  Constants

_LIT(KTextConsoleTitle, "Console");
_LIT(KTextFailed, " failed, leave code = %d");
_LIT(KTextPressAnyKey, " [press any key]\n");
_LIT(KLogFile, "c:\\CenrepTest.txt");
//  Global Variables

LOCAL_D CConsoleBase* console; // write all messages to this
LOCAL_D TBool ReadCommandLineToArrayL(TPtr& aCmdptr, RPointerArray<HBufC>& aArrayOfArgs);
LOCAL_D TBool gWaitForKeyPress = ETrue;
LOCAL_D TBool gLogResult = ETrue;

//  Local Functions

LOCAL_C void DoLogResultL(TInt aResult);

LOCAL_C void MainL()
	{
	//Get the parameters that have been entered
	HBufC* cmdBuf = HBufC::NewLC(User::CommandLineLength());
	
	TPtr cmdPtr = cmdBuf->Des();
	User::CommandLine(cmdPtr);
	cmdPtr.TrimAll();
	
	RPointerArray<HBufC> argsArray; 
	CleanupStack::PushL( TCleanupItem(CCommandHandler::ResetAndDestroyPtrArray, &argsArray) );
	
	RArray<TPtrC> argsPtr;	
	CleanupClosePushL(argsPtr);
	
	//Parse parameter into array and check for verbosity
	TBool verbose = ReadCommandLineToArrayL(cmdPtr, argsArray);
	
	if(argsArray.Count() == 0)
		verbose = ETrue;
	else
		for(TInt i=0; i<argsArray.Count(); ++i)
			argsPtr.AppendL(argsArray[i]->Des());
	
	// Create a CCmdLineOutput object which deals with any output messages
	//CCmdLineOutput* console = Ulogger::CCmdLineOutput::NewLC(verbose);
	CCommandHandler* cmdHandler = CCommandHandler::NewLC(console);
	
	TRAPD(result, cmdHandler->HandleCommandL(argsPtr)); // Process the commands as entered

	
	if ( gLogResult ) {
		DoLogResultL(result);
	}

	User::LeaveIfError(result);
		
	CleanupStack::PopAndDestroy(4); //cmdHandler, argsPtr, argsArray, cmdBuf, 

	}

/**
 * Write the 
 */
LOCAL_C void DoLogResultL(TInt aResult) 
	{
	RFs fs;
	User::LeaveIfError(fs.Connect());
	CleanupClosePushL(fs);
	RFile file;
	User::LeaveIfError(file.Replace(fs,KLogFile, EFileWrite));
	CleanupClosePushL(file);
	TBuf8<32> buf;
	buf.AppendNum(aResult);
	file.Write(buf);
	CleanupStack::PopAndDestroy(2);
	}

/**
 * Prase command line args into an array
 */
LOCAL_C TBool ReadCommandLineToArrayL(TPtr& aCmdptr, RPointerArray<HBufC>& aArrayOfArgs)
{
	TInt searchRes;
	
	do
	{
		//find comas and insert spaces instead
		searchRes = aCmdptr.Find(KComa);
		if(searchRes >= 0) 
			aCmdptr.Replace(searchRes, 1, KSpace);
	}
	while(searchRes != KErrNotFound);

	//check for verbose mode and fill array with tokens
	TBool verbose = EFalse;
	TLex argv(aCmdptr);
    for (TInt i = 0; !argv.Eos() ; i++)
	{
		TPtrC token = argv.NextToken();
		HBufC* argument = HBufC::NewLC(token.Length()+8); //8 is for any additional characters that might be added later
		TPtr argPtr(argument->Des());
		argPtr.Copy(token);
		
		if(!argPtr.Mid(0,1).Compare(KCmdIndicator)) //make sure this is an option token (e.g. -lfv)
			{			
			TInt f = argPtr.Find(KCmdVerbose);
			if(f >= 0)
				{
				verbose = ETrue;
				argPtr.Delete(f, 1); //remove 'v' verbose indicator as it is not needed any more
				}				
			f = argPtr.Find(KCmdNoWait);
			if(f >= 0)
				{
				gWaitForKeyPress = EFalse;
				argPtr.Delete(f, 1); //remove 'v' verbose indicator as it is not needed any more
				}				
			}
		//append argument into array, exception is a '-v', 
		//where 'v' will be removed and we don't want to append just '-'
		if(argPtr.Length() == 1 && !argPtr.Mid(0,1).Compare(KCmdIndicator)) 
			CleanupStack::PopAndDestroy(); //argument
		else
			{
			CleanupStack::Pop(); //argument
			aArrayOfArgs.AppendL(argument);
			}
	}

	return verbose;
}

LOCAL_C void DoStartL()
	{
	// Create active scheduler (to run active objects)
	CActiveScheduler* scheduler = new (ELeave) CActiveScheduler();
	CleanupStack::PushL(scheduler);
	CActiveScheduler::Install(scheduler);

	MainL();

	// Delete active scheduler
	CleanupStack::PopAndDestroy(scheduler);
	}

//  Global Functions

GLDEF_C TInt E32Main()
	{
	// Create cleanup stack
	__UHEAP_MARK;
	CTrapCleanup* cleanup = CTrapCleanup::New();

	// Create output console
	TRAPD(createError, console = Console::NewL(KTextConsoleTitle, TSize(
			KConsFullScreen, KConsFullScreen)));
	if (createError)
		return createError;

	// Run application code inside TRAP harness, wait keypress when terminated
	TRAPD(mainError, DoStartL());
	if (mainError)
		console->Printf(KTextFailed, mainError);
	console->Printf(KTextPressAnyKey);
	if ( gWaitForKeyPress ) {
		console->Getch();
	}

	delete console;
	delete cleanup;
	__UHEAP_MARKEND;
	return KErrNone;
	}

