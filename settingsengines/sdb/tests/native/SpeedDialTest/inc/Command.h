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
 Name		: Command.h
 Author	  : 
 Version	 : 1.0
 Copyright   : Your copyright notice
 Description : CCommand declaration
 ============================================================================
 */

#ifndef COMMAND_H
#define COMMAND_H

// INCLUDES
#include <e32std.h>
#include <e32base.h>
#include <badesca.h>
#include <spdtestconst.h>

// CLASS DECLARATION

/**
 *  CCommand
 * 
 */
class CCommand : public CBase
	{
public:
	// Constructors and destructor

	/**
	 * Destructor.
	 */
	~CCommand();

	/**
	 * Two-phased constructor.
	 */
	static CCommand* NewL(TCommandId aCommand, CDesC16ArrayFlat* aParams);

	/**
	 * Two-phased constructor.
	 */
	static CCommand* NewLC(TCommandId aCommand, CDesC16ArrayFlat* aParams);
	
	/**
	 * return command id
	 */
	const TCommandId CommandId();
	
	/**
	 * return command params
	 */
	const CDesC16ArrayFlat* CommandParams();
	

private:

	/**
	 * Constructor for performing 1st stage construction
	 */
	CCommand();

	/**
	 * EPOC default constructor for performing 2nd stage construction
	 */
	void ConstructL(TCommandId aCommand, CDesC16ArrayFlat* aParams);
	
private:
	
	TCommandId iCommandId;
	CDesC16ArrayFlat* iParams;
	
	};

#endif // COMMAND_H
