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
 Name		: CommandLineHandler.cpp
 Author	  : 
 Version	 : 1.0
 Copyright   : Your copyright notice
 Description : CCommandHandler implementation
 ============================================================================
 */

#include "CommandHandler.h"
#include "cenreptestconst.h"


void CCommandHandler::ResetAndDestroyPtrArray(TAny* aPtr)
	{
	(STATIC_CAST(RPointerArray<HBufC>*, aPtr))->ResetAndDestroy();
	(STATIC_CAST(RPointerArray<HBufC>*, aPtr))->Close();
	}

CCommandHandler::CCommandHandler(CConsoleBase* aConsole) : iConsole(aConsole)
	{
	// No implementation required
	}

CCommandHandler::~CCommandHandler()
	{
	
	}

CCommandHandler* CCommandHandler::NewLC(CConsoleBase* aConsole)
	{
	CCommandHandler* self = new (ELeave) CCommandHandler(aConsole);
	CleanupStack::PushL(self);
	self->ConstructL();
	return self;
	}

CCommandHandler* CCommandHandler::NewL(CConsoleBase* aConsole)
	{
	CCommandHandler* self = CCommandHandler::NewLC(aConsole);
	CleanupStack::Pop(); // self;
	return self;
	}

void CCommandHandler::ConstructL()
	{

	}

void CCommandHandler::HandleCommandL(const RArray<TPtrC>& aArgs)
	{
	
	RArray<TPtrC> cmdArgs;
	CleanupClosePushL(cmdArgs);
	
	if( aArgs.Count() < 2 )
	{
	HandleCommandError(EInvalidCmdArgs);
	User::Leave(KErrArgument);
	}
	
	//copy command arguments
	for (int index = 2; index < aArgs.Count(); ++index)
		{
		cmdArgs.Append(aArgs[index]);
		}
	
	RBuf command;
	CleanupClosePushL(command);
	command.CreateL(aArgs[0]);
	command.LowerCase();
	if(command.Find(KCmdIndicator) == 0)
		{
		if(command.Mid(1).Match(KCmdMode()) == 0)
			{
			RBuf mode;
			CleanupClosePushL(mode);
			mode.CreateL(aArgs[1]);
			mode.LowerCase();
			if(mode.Match(KModeCreate) == 0)
				{
				iConsole->Write(_L("Executing mode : create"));
				iConsole->Write(_L("\n"));
				//create setting in central repositiory
				CreateSettingInRepositoryL(cmdArgs);
				}
			else if(mode.Match(KModeValidate) == 0)
				{
				iConsole->Write(_L("Executing mode : validate"));
				iConsole->Write(_L("\n"));
				//validate setting in cenrep
				ValidateSettingInRepositoryL(cmdArgs);
				}
			else
				{
				//Repote error unknown mode
				HandleCommandError(EInvalidMode);
				}
			CleanupStack::PopAndDestroy(&mode);
			}
		else
			{
			// report error invalid command 
			HandleCommandError(EInvalidCmdArgs);
			}
		}
	else
		{
		// report error missing command
		HandleCommandError(EInvalidCmdArgs);
		}
	CleanupStack::PopAndDestroy(2);
	}
	
void CCommandHandler::HandleCommandError(TInt aError)
{
	switch(aError)
	{
		case EInvalidMode:
		case EInvalidCmdArgs:
			PrintUsage();
			break;
	}
}

TUint CCommandHandler::HexDesToUint(const TPtrC& aDes)
{
    TLex lex;
    lex.Assign(aDes);
    TUint intVal;
    lex.Val(intVal, EHex);
    return intVal;
}

TInt CCommandHandler::DesToInt(const TPtrC & aDes)
{
	TLex lex;
	lex.Assign(aDes);
	TInt realVal;
	lex.Val(realVal);
	return realVal;
}

TReal CCommandHandler::DesToReal(const TPtrC & aDes)
{
	TLex lex;
	lex.Assign(aDes);
	TReal realVal;
	lex.Val(realVal);
	return realVal;
}

void CCommandHandler::CreateSettingInRepositoryL(const RArray<TPtrC> & aCmdArgs)
{
	//Create repository object and set setting
	TPtrC repositoryUid = aCmdArgs[0]; // repository UID in hex format
	TPtrC settingId		= aCmdArgs[1]; // setting UID in hex format
	TPtrC settingType	= aCmdArgs[2]; // setting data format
	TPtrC settingVal	= aCmdArgs[3]; // setting value
	
	//print info message
	iConsole->Write(_L("Reading repository "));
	iConsole->Write(repositoryUid);
	
	CRepository *repository =  CRepository::NewL(HexDesToUid(repositoryUid));
	CleanupStack::PushL(repository);
	if(repository != NULL)
	{
		iConsole->Write(_L(" ...repository exists \n"));
		//Set setting here
		TInt err = repository->Create(HexDesToUint(settingId), DesToInt(settingVal));
		if(KErrAlreadyExists == err)
		{
			User::LeaveIfError(repository->Delete(HexDesToUint(settingId)));
			err = repository->Create(HexDesToUint(settingId), DesToInt(settingVal));
		}
		if(KErrNone == err)
		{
			iConsole->Write(_L("Setting created, Id : "));
			iConsole->Write(settingId);
		}
		else
		{
			User::Leave(err);
		}
	}
	CleanupStack::PopAndDestroy(repository);
}

void CCommandHandler::ValidateSettingL(CRepository *& repository, TPtrC settingId, TPtrC settingType, TPtrC settingVal)
{

	iConsole->Write(_L(" ...repository exists \n"));
	
	iConsole->Write(_L("Reading setting, Id : "));
	iConsole->Write(settingId);
	
	if(settingType.Match(KTypeInt) == 0)
	{
		ValidateIntValueL(repository, settingId, settingVal);
	}
	else if(settingType.Match(KTypeReal) == 0)
	{
		ValidateRealValueL(repository, settingId, settingVal);
	}
	else if(settingType.Match(KTypeString) == 0) 
	{
		ValidateStringValueL(repository, settingId, settingVal);
	}
	else if(settingType.Match(KTypeString8) == 0) 
	{
		ValidateString8ValueL(repository, settingId, settingVal);
	}
}

void CCommandHandler::ValidateIntValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal)
{
	TInt readVal;
	User::LeaveIfError(repository->Get(DesToInt(settingId), readVal));
	if(readVal == HexDesToUint(settingVal))
	{
		iConsole->Write(_L(" ...setting exists"));
	}
	else
	{
		User::Leave(KErrCorrupt);	
	}
}

void CCommandHandler::ValidateRealValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal)
{
	TReal readVal;
	User::LeaveIfError(repository->Get(DesToInt(settingId), readVal));
	if(readVal == DesToReal(settingVal))
	{
		iConsole->Write(_L(" ...setting exists"));
	}
	else
	{
		User::Leave(KErrCorrupt);	
	}
}

void CCommandHandler::ValidateStringValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal)
{
	TBuf<1024> string;
	User::LeaveIfError(repository->Get(DesToInt(settingId), string));
	if(string.Match(settingVal) == 0)
	{
		iConsole->Write(_L(" ...setting exists"));
	}
	else
	{
		User::Leave(KErrCorrupt);	
	}
}

void CCommandHandler::ValidateString8ValueL(CRepository *& repository, TPtrC settingId, TPtrC settingVal)
{
	TBuf8<1024> buf;
	User::LeaveIfError(repository->Get(DesToInt(settingId), buf));
	TBuf<1024> string;
	string.Copy(buf);
	if(string.Match(settingVal) == 0)
	{
		iConsole->Write(_L(" ...setting exists"));
	}
	else
	{
		User::Leave(KErrCorrupt);	
	}
}

void CCommandHandler::ValidateSettingInRepositoryL(const RArray<TPtrC> & aCmdArgs)
{
	//Create repository object and validate setting.
	TPtrC repositoryUid = aCmdArgs[0]; // repository UID in hex format
	TPtrC settingId		= aCmdArgs[1]; // setting UID in hex format
	TPtrC settingType	= aCmdArgs[2]; // setting data format
	TPtrC settingVal 	= aCmdArgs[3];
	
	//print info message
	iConsole->Write(_L("Reading repository "));
	iConsole->Write(repositoryUid);
	
	CRepository *repository =  CRepository::NewL(HexDesToUid(repositoryUid));
	CleanupStack::PushL(repository);
	if(repository != NULL)
	{
		ValidateSettingL(repository, settingId, settingType, settingVal);
	}
    CleanupStack::PopAndDestroy(repository);
}

TUid CCommandHandler::HexDesToUid(const TPtrC & aDes)
{
	return TUid::Uid(HexDesToUint(aDes));
}

void CCommandHandler::PrintUsage()
{
	iConsole->Write(_L("Invalid command or mode switch.\n"));
	iConsole->Write(_L("Usage:\n"));
	iConsole->Write(_L("CenrepTest -m <create|validate> <Repository Id> <Setting Id> <Setting Type> <Setting Value>\n"));
}















