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

#include "SdbTest.h"
#include "ViewEngine.h"

#include <cntdb.h>
#include <cntitem.h>
#include <cntfldst.h>
#include <cntview.h>
#include <cntviewbase.h>

extern void RegisterTestL(const TDesC&, TTestFunction);


// //
// Add a test function prototype here 
int FilterTestL(RSdbTest& aTest);

void FilterCountL(RSdbTest& aTest);

CContactDatabase* OpenDefaultDbLC(RSdbTest& aTest);
TInt32 DesToInt32(const TPtrC& aDes);

// //
// Register your test here 
//
void RegisterTestsL()
	{
	_LIT(KExampleFilterTestName, "FilterTest");
	RegisterTestL(KExampleFilterTestName, &FilterTestL);
	}

int FilterTestL(RSdbTest& aTest)
	{
	CCommandLineArguments* cmdLine = aTest.CommandLineArgumentsL();

	CDbViewEngine* viewEng = CDbViewEngine::NewL(&aTest, DesToInt32(cmdLine->Arg(2)), DesToInt32(cmdLine->Arg(3)));
	CleanupStack::PushL(viewEng);
	viewEng->StartL();
	CActiveScheduler::Start();
	aTest.AsyncEndL();
	CleanupStack::PopAndDestroy(viewEng);
	
	return aTest.GetLastError();
	}


CContactDatabase* OpenDefaultDbLC(RSdbTest& aTest)
{
    TBuf<64> dbName;
    CContactDatabase::GetDefaultNameL(dbName);
    aTest.Printf(_L("Reading database: %S\n"), &dbName);
    CContactDatabase *iDatabase = CContactDatabase::OpenL(dbName);
    CleanupStack::PushL(iDatabase);
    return iDatabase;
}

TInt32 DesToInt32(const TPtrC& aDes)
{
    TLex lex;
    lex.Assign(aDes);
    TInt32 intVal;
    lex.Val(intVal);
    return intVal;
}




