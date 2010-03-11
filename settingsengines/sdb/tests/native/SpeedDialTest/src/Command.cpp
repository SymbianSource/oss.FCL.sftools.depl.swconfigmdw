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
 Name		: Command.cpp
 Author	  : 
 Version	 : 1.0
 Copyright   : Your copyright notice
 Description : CCommand implementation
 ============================================================================
 */

#include "Command.h"

CCommand::CCommand() : iCommandId(EInvalid), iParams(NULL)
	{
	// No implementation required
	}

CCommand::~CCommand()
	{
	if(iParams)
		{
		iParams->Reset();
		}
	}

CCommand* CCommand::NewLC(TCommandId aCommand, CDesC16ArrayFlat* aParams)
	{
	CCommand* self = new (ELeave) CCommand();
	CleanupStack::PushL(self);
	self->ConstructL(aCommand, aParams);
	return self;
	}

CCommand* CCommand::NewL(TCommandId aCommand, CDesC16ArrayFlat* aParams)
	{
	CCommand* self = CCommand::NewLC(aCommand, aParams);
	CleanupStack::Pop(); // self;
	return self;
	}

void CCommand::ConstructL(TCommandId aCommand, CDesC16ArrayFlat* aParams)
	{
		iCommandId = aCommand;
		iParams = aParams;
	}

TCommandId CCommand::CommandId()
	{
	return iCommandId;
	}

CDesC16ArrayFlat* CCommand::CommandParams()
	{
	return iParams;
	}
