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
#include "spdtestconst.h"

void CCommandHandler::ResetAndDestroyPtrArray(TAny* aPtr)
	{
	(STATIC_CAST(RPointerArray<HBufC>*, aPtr))->ResetAndDestroy();
	(STATIC_CAST(RPointerArray<HBufC>*, aPtr))->Close();
	}

CCommandHandler::CCommandHandler(CConsoleBase* aConsole) : iConsole(aConsole), iContactDb(0)
	{
	// No implementation required
	}

CCommandHandler::~CCommandHandler()
	{
	if(iContactDb)
		{
		delete iContactDb;
		}
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
				 //execute createIni command
				CreateSpeedDialIniL(cmdArgs);
				}
			else if(mode.Match(KModeValidate) == 0)
				{
				iConsole->Write(_L("Executing mode : validate"));
				iConsole->Write(_L("\n"));
				// execute validateIni command
				ValidateSpeedDialIniL(cmdArgs);
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
			
		case EInvalideCntId:
		case EEmptyDatabase:
			PrintDatabaseError(aError);
			break;
			
		default:
			PrintCntModelError(aError); 
		}
	}

TInt32 CCommandHandler::DesToInt32(const TPtrC& aDes)
{
    TLex lex;
    lex.Assign(aDes);
    TInt32 intVal;
    lex.Val(intVal);
    return intVal;
}

void CCommandHandler::CreateSpeedDialIniL(const RArray<TPtrC> & aCmdArgs)
	{
	
	//Check if enough arguments are supplied 
	if(aCmdArgs.Count() < 2)
		{
		HandleCommandError(EInvalidCmdArgs);
		User::Leave(KErrArgument);
		}
	
	//print speeddial index
	iConsole->Write(_L("SpeedDail Index : "));
	iConsole->Write(aCmdArgs[0]);
	iConsole->Write(_L("\n"));
	
	//print contact id
	iConsole->Write(_L("Contact Id : "));
	iConsole->Write(aCmdArgs[1]);
	iConsole->Write(_L("\n"));
		
	//Initialise contact model
	iContactDb = OpenDefaultDb();
	
	//Read contact from database
	TInt contactsCount = iContactDb->CountL();
	if( contactsCount > 0 )
		{
		// Get the contact
		CContactItem* spdContact = iContactDb->OpenContactL(DesToInt32(aCmdArgs[1]));
		CleanupStack::PushL(spdContact);
		CContactItemFieldSet& fieldSet = spdContact->CardFields();
		TInt fieldIndex = fieldSet.Find(KUidContactFieldPhoneNumber);
		CContactItemField& field = fieldSet[fieldIndex];
		if(!field.LabelUnspecified())
			{
			iConsole->Write(field.Label());
			iConsole->Write(_L("\n"));
			}
		CContactTextField* fieldData = static_cast<CContactTextField*>(field.Storage());
		CleanupStack::PushL(fieldData);
		iConsole->Write(fieldData->Text());
		iConsole->Write(_L("\n"));

		TInt pos = DesToInt32(aCmdArgs[0]);
		
		//set speed dial functions
		iContactDb->SetFieldAsSpeedDialL(*spdContact, fieldIndex, pos);
		iConsole->Write(_L("Speed dial ini file created.\n"));
		CleanupStack::PopAndDestroy(2);
		}
	else
		{
		
		}

	}

CContactDatabase* CCommandHandler::OpenDefaultDb()
{
    TBuf<64> dbName;
    CContactDatabase::GetDefaultNameL(dbName);
    iConsole->Write(_L("Reading database : "));
    iConsole->Write(dbName);
    iConsole->Write(_L("\n"));
    //Open default database
    return CContactDatabase::OpenL(dbName);
}

void CCommandHandler::ValidateSpeedDialIniL(const RArray<TPtrC>& aCmdArgs)
	{
	//Check if enough arguments are supplied 
	if(aCmdArgs.Count() < 2)
		{
		HandleCommandError(EInvalidCmdArgs);
		User::Leave(KErrArgument);
		}
	
	//print speeddial index
	iConsole->Write(_L("SpeedDail Index : "));
	iConsole->Write(aCmdArgs[0]);
	iConsole->Write(_L("\n"));
	
	//print contact id
	iConsole->Write(_L("Contact Id : "));
	iConsole->Write(aCmdArgs[1]);
	iConsole->Write(_L("\n"));
	    
	iContactDb = OpenDefaultDb();
	
	//Read contact from database
	TInt contactsCount = iContactDb->CountL();
	if( contactsCount > 0 )
		{
		TContactItemId contactId = DesToInt32(aCmdArgs[1]);
		CContactItem* spdContact = iContactDb->ReadContactL(contactId);
		CleanupStack::PushL(spdContact);
		CContactItemFieldSet& fieldSet = spdContact->CardFields();
		TInt fieldIndex = fieldSet.Find(KUidContactFieldPhoneNumber);
		CContactItemField& field = fieldSet[fieldIndex];
		if(field.IsSpeedDial())
			{
			iConsole->Write(_L("Speed dial field : "));
			if(!field.LabelUnspecified())
				{
				iConsole->Write(field.Label());
				iConsole->Write(_L(", contents : "));
				}
			CContactTextField* fieldData = static_cast<CContactTextField*>(field.Storage());
			iConsole->Write(fieldData->Text());
			iConsole->Write(_L("\n"));
			
			TInt pos = DesToInt32(aCmdArgs[0]);
				
			TBuf<32> expectedContactNumber;
			if(aCmdArgs.Count() == 3)
				{
				expectedContactNumber=aCmdArgs[2];
				}
			else
				{
				expectedContactNumber=fieldData->Text();
				}
			//set speed dial functions
			if(isSpeedDialSetForContact(pos, contactId, expectedContactNumber))
				{
				iConsole->Write(_L("Speed dial is set to position : "));
				iConsole->Write(aCmdArgs[0]);
				iConsole->Write(_L(" for specified contact. \n"));
				}
			else
				{
				iConsole->Write(_L("Speed dial position or number is wrong. \n"));
				User::Leave(KErrNotFound);
				}
			}
		else
			{ 
			// Not a speed dial report error
			iConsole->Write(_L("Specified contact is not a speed dial contact. \n"));
			User::Leave(KErrNotFound);
			}
		CleanupStack::PopAndDestroy(spdContact);
		}
	else
		{
		HandleCommandError(EEmptyDatabase);
		}
	}

bool CCommandHandler::isSpeedDialSetForContact(TInt speedDialValue, TInt expectedContactID, TBuf<32> expectedContactNumber)
	{
		TBuf<32> spdPhoneNum;
		TContactItemId spdContactId = iContactDb->GetSpeedDialFieldL(speedDialValue, spdPhoneNum);
		_LIT(Kformat," %d");
		TBuf<32> msg;
		msg.Format(Kformat,spdContactId);
		iConsole->Write(_L("Recovered Speed Dial Contact ID:"));
		iConsole->Write(msg);
		iConsole->Write(_L("\n"));
		iConsole->Write(_L("Expected Phone Number:"));
		iConsole->Write(expectedContactNumber);
		iConsole->Write(_L("\n"));
		iConsole->Write(_L("Recovered Phone Number:"));
		iConsole->Write(spdPhoneNum);
		iConsole->Write(_L("\n"));
		return(spdContactId == expectedContactID && spdPhoneNum.Match(expectedContactNumber) == 0);
	}

void CCommandHandler::PrintUsage()
	{
	iConsole->Write(_L("Invalid command or mode switch.\n"));
	iConsole->Write(_L("Usage:\n"));
	iConsole->Write(_L("SpeedDialTest -m <create|validate> <speed dial index> <contact id in db>\n"));
	}

void CCommandHandler::PrintCntModelError(TInt /*aCntModelError*/)
	{
	//TODO
	}

void CCommandHandler::PrintDatabaseError(TInt aDatabaseError)
{
	iConsole->Write(_L("Not a valid contact id or database is empty.\n"));
	User::Leave(KErrArgument);
}










