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
#include <centralrepository.h> 

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
	
	void CreateSettingInRepositoryL(const RArray<TPtrC>& aCmdArgs);
	void ValidateSettingInRepositoryL(const RArray<TPtrC>& aCmdArgs);
    
    TUid HexDesToUid(const TPtrC& aDes);
    TUint HexDesToUint(const TPtrC& aDes);
    TInt DesToInt(const TPtrC & aDes);
    TReal DesToReal(const TPtrC& aDes);
    
    void HandleCommandError(TInt aError);
    void PrintUsage();
    
    void ValidateSettingL(CRepository *& repository, TPtrC settingId, TPtrC settingType, TPtrC settingVal);
    void ValidateIntValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal);
    void ValidateRealValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal);
    void ValidateStringValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal);
    void ValidateString8ValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal);
    
	
private:
	
	CConsoleBase* iConsole;
	};

#endif // COMMANDLINEHANDLER_H
