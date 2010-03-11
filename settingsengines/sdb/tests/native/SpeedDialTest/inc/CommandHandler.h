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
 Name		: CommandLineHandler.h
 Author	  : 
 Version	 : 1.0
 Copyright   : Your copyright notice
 Description : CCommandHandler declaration
 ============================================================================
 */

#ifndef COMMANDLINEHANDLER_H
#define COMMANDLINEHANDLER_H

// INCLUDES
#include <e32std.h>
#include <e32base.h>
#include <e32cons.h>
#include <cntdb.h>
#include <cntitem.h>
#include <cntfldst.h>

// CLASS DECLARATION

/**
 *  CCommandHandler
 * 
 */
class CCommandHandler : public CBase
	{
public:
	// Constructors and destructor

	/**
	 * Destructor.
	 */
	~CCommandHandler();

	/**
	 * Two-phased constructor.
	 */
	static CCommandHandler* NewL(CConsoleBase* aConsole);

	/**
	 * Two-phased constructor.
	 */
	static CCommandHandler* NewLC(CConsoleBase* aConsole);
	
	/**
	 * Desrtroy allocated pointers and close the array 
	 */
	static void ResetAndDestroyPtrArray(TAny* aPtr);
	
	/**
	 * 
	 */
	void HandleCommandL(const RArray<TPtrC>& aArgs);
	
private:

	/**
	 * Constructor for performing 1st stage construction
	 */
	CCommandHandler(CConsoleBase* aConsole);

	/**
	 * EPOC default constructor for performing 2nd stage construction
	 */
	void ConstructL();
	
	void CreateSpeedDialIniL(const RArray<TPtrC>& aCmdArgs);
	void ValidateSpeedDialIniL(const RArray<TPtrC>& aCmdArgs);
    TInt32 DesToInt32(const TPtrC& aDes);
    void HandleCommandError(TInt aError);
    bool isSpeedDialSetForContact(TInt speedDialValue, TInt expectedContactID, TBuf<32> expectedContactNumber);
    void PrintUsage();
    void PrintCntModelError(TInt aCntModelError);
    void PrintDatabaseError(TInt aDatabaseError);
    CContactDatabase* OpenDefaultDb();

	
private:
	
	CConsoleBase* iConsole;
	CContactDatabase* iContactDb;

	};

#endif // COMMANDLINEHANDLER_H
