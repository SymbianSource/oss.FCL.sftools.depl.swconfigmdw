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
 Name		: SdbTestFramework.cpp
 Author	  : 
 Copyright   : Your copyright notice
 Description : CSdbTestFramework DLL source
 ============================================================================
 */

//  Include Files  

#include <bacline.h>
#include <e32keys.h>
#include "SdbTestFramework.h"	// CSdbTestFramework

const TInt KResultNotWritten = -100000; 
_LIT(KDefaultOutputFileName, "c:\\SdbTestOut.txt");
_LIT(KDefaultTitle, "SdbTest");
//  Member Functions

EXPORT_C RSdbTest::RSdbTest()
: iTest(RTest(KDefaultTitle)), iCommandLineArguments(NULL), 
  iEnded(EFalse), iClosed(EFalse), iDebug(EFalse)
	{
	iOutputFileName.Copy(KDefaultOutputFileName);
	}

EXPORT_C RSdbTest::RSdbTest(const TDesC& aTitle)
: iTest(RTest(aTitle)), iCommandLineArguments(NULL), 
  iEnded(EFalse), iClosed(EFalse), iDebug(EFalse)
	{
	iOutputFileName.Copy(KDefaultOutputFileName);
	iEnded = EFalse;
	iClosed = EFalse;
	}

EXPORT_C void RSdbTest::Title()
	{
	iTest.Title();
	}

EXPORT_C void RSdbTest::CloseL()
	{
	if ( ! iClosed ) 
		{
		if ( !iEnded ) 
			{
			EndL(KErrNone);
			}
		iTest.Close();
		iFs.Close();
		if ( iCommandLineArguments != NULL )
			{
			delete iCommandLineArguments;
			}
		iClosed = ETrue;
		}
	}

EXPORT_C void RSdbTest::StartL(const TDesC &aHeading)
	{
	User::LeaveIfError(iFs.Connect());
	TInt error = iFs.Delete(iOutputFileName);
	if ( error != KErrNone && error != KErrNotFound ) 
		{
		User::Leave(error);
		}
	iTest.Start(aHeading);
	}

EXPORT_C void RSdbTest::Next(const TDesC &aHeading)
	{
	iTest.Next(aHeading);
	}

EXPORT_C void RSdbTest::EndL(TInt aExitValue)
	{
	if ( iEnded )
		{
		return;
		}
	RFile file;
	User::LeaveIfError(file.Create(iFs,iOutputFileName, EFileWrite));
	CleanupClosePushL(file);
	TBuf8<32> buf;
	buf.AppendNum(aExitValue);
	User::LeaveIfError(file.Write(buf));
	CleanupStack::PopAndDestroy(1);
	iTest.End();
	iEnded = ETrue;
	}
	
EXPORT_C void RSdbTest::Printf(TRefByValue<const TDesC> aFmt,...)
	{
	VA_LIST list;
	VA_START(list, aFmt);
	TBuf<0x100> buf;
	buf.AppendFormatList(aFmt, list);
	Console()->Write(buf);
	}

EXPORT_C TKeyCode RSdbTest::Getch()
	{
	if ( iDebug ) 
		{
		return iTest.Getch();
		}
	else 
		{
		return EKeyNull;
		}
	}

EXPORT_C void RSdbTest::SetOutputFileName(const TDesC& aFileName)
	{
	iOutputFileName.Copy(aFileName);
	}

EXPORT_C TDesC& RSdbTest::GetOutputFileName()
	{
	return iOutputFileName;
	}

EXPORT_C CConsoleBase* RSdbTest::Console() const
	{
	return iTest.Console();
	}
	
EXPORT_C void RSdbTest::SetConsole(CConsoleBase* aConsole)
	{
	iTest.SetConsole(aConsole);
	}

EXPORT_C TBool RSdbTest::Logged() const
	{
	return iTest.Logged();
	}
	
EXPORT_C void RSdbTest::SetLogged(TBool aToLog)
	{
	iTest.SetLogged(aToLog);
	}

EXPORT_C void RSdbTest::AssertTrueL(TBool aValue)
	{
	AssertTrueL(aValue, _L("Test failed. No further info available"));
	}

EXPORT_C void RSdbTest::AssertNotErrorL(TInt aValue)
	{
	AssertNotErrorL(aValue, _L("Test failed. No further info available"));
	}

EXPORT_C void RSdbTest::AssertTrueL(TBool aValue, TInt aLine)
	{
	TBuf<64> buf;
	buf.Copy(_L("Test failed at line "));
	buf.AppendNum(aLine);
	AssertTrueL(aValue, buf);
	}

EXPORT_C void RSdbTest::AssertNotErrorL(TInt aValue, TInt aLine)
	{
	TBuf<64> buf;
	buf.Copy(_L("Test failed at line "));
	buf.AppendNum(aLine);
	AssertNotErrorL(aValue, buf);
	}

EXPORT_C void RSdbTest::AssertTrueL(TBool aValue, const TDesC& aComment, TInt aLine)
	{
	TBuf<256> buf;
	buf.Copy(_L("Test failed at line "));
	buf.AppendNum(aLine);
	buf.Append(_L(": "));
	buf.Append(aComment);
	AssertTrueL(aValue, buf);
	}

EXPORT_C void RSdbTest::AssertNotErrorL(TInt aValue, const TDesC& aComment, TInt aLine)
	{
	TBuf<256> buf;
	buf.Copy(_L("Test failed at line "));
	buf.AppendNum(aLine);
	buf.Append(_L(": "));
	buf.Append(aComment);
	AssertNotErrorL(aValue, buf);
	}

EXPORT_C void RSdbTest::AssertTrueL(TBool aValue, const TDesC& aComment)
	{
	if ( ! aValue ) 
		{
		iTest.Printf(aComment);
		EndL(KErrGeneral);
		User::Leave(KErrGeneral);
		}
	}

EXPORT_C void RSdbTest::AssertNotErrorL(TInt aValue, const TDesC& aComment)
	{
	if ( aValue != KErrNone ) 
		{
		iTest.Printf(aComment);
		EndL(aValue);
		User::LeaveIfError(aValue);
		}
	}

EXPORT_C CCommandLineArguments* RSdbTest::CommandLineArgumentsL()
	{
	if ( iCommandLineArguments == NULL )
		{
		iCommandLineArguments = CCommandLineArguments::NewL();
		}
	return iCommandLineArguments; 
	}

EXPORT_C void RSdbTest::SetDebugMode(TBool aDebug)
	{
	iDebug = aDebug;
	}
