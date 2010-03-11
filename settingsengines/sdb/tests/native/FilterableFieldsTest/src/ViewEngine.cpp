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

#include "ViewEngine.h"

CDbViewEngine::CDbViewEngine(RSdbTest* aObserver) :
	CActive(EPriorityStandard), iObserver(aObserver), iDb(0),
			iFilteredViewExists(EFalse) // Standard priority
	{
	}

CDbViewEngine* CDbViewEngine::NewLC(RSdbTest* aObserver,
		const TInt aFilter, TInt aReturnCount)
	{
	CDbViewEngine* self = new (ELeave) CDbViewEngine(aObserver);
	CleanupStack::PushL(self);
	self->ConstructL(aFilter, aReturnCount);
	return self;
	}

CDbViewEngine* CDbViewEngine::NewL(RSdbTest* aObserver,
		const TInt aFilter, TInt aReturnCount)
	{
	CDbViewEngine* self = CDbViewEngine::NewLC(aObserver, aFilter, aReturnCount);
	CleanupStack::Pop(); // self;
	return self;
	}

void CDbViewEngine::ConstructL(const TInt aFilter, TInt aReturnCount)
	{
	iDb = OpenDefaultDbL();
	iSortOrder_1.AppendL(KUidContactFieldGivenName);
	iSortOrder_1.AppendL(KUidContactFieldFamilyName);
	iSortOrder_1.AppendL(KUidContactFieldCompanyName);
	SetFilterTypeL(aFilter);
	iExpectedContactMatch=aReturnCount;
	CActiveScheduler::Add(this); // Add to scheduler

	}

CDbViewEngine::~CDbViewEngine()
	{

	if (iFilterView)
		iFilterView->Close(*this);

	if (iNamedRemoteView)
		iNamedRemoteView->Close(*this);

	iSortOrder_1.Close();

	if (iDb)
		delete iDb;

	}

CContactDatabase* CDbViewEngine::OpenDefaultDbL()
	{
	TBuf<64> dbName;
	CContactDatabase::GetDefaultNameL(dbName);
	return CContactDatabase::OpenL(dbName);
	}

void CDbViewEngine::DoCancel()
	{

	}

void CDbViewEngine::RunL()
	{
	if (!iNamedRemoteViewExists)
		{
		iNamedRemoteView = CContactNamedRemoteView::NewL(*this,
				KRemoteViewName, *iDb, iSortOrder_1, EContactsOnly);
		}
	else if (iNamedRemoteViewExists)
		{
		//iTestStep.INFO_PRINTF1(_L("Creating the filtered view "));
		//iInstrumentation.RaiseInstrumentationEventNotificationL(MTestInstrumentation::EPointContactsFilteringStart);
		//iFilterType = CContactDatabase::EPhonable;
		iFilterView = CContactFilteredView::NewL(*this, *iDb,
				*iNamedRemoteView, iFilterType);

		}

	}

void CDbViewEngine::HandleContactViewEvent(const CContactViewBase& /*aView*/,
		const TContactViewEvent& aEvent)
/**
 invoked by the active object mechanism
 @param active object handles
 @leave system wide error codes
 */
	{
	//iTestStep.INFO_PRINTF1(_L("Entered the HandleContactViewEvent callback"));
	if (aEvent.iEventType == TContactViewEvent::EReady)
		{
		//check if the call back is invoked by remote view instantiation.
		if (!iNamedRemoteViewExists)
			{
			//      iInstrumentation.RaiseInstrumentationEventNotificationL(MTestInstrumentation::EPointContactsRemoteViewEnd);
			iNamedRemoteViewExists = ETrue;
			StartL();
			}
		else if (iNamedRemoteViewExists)
			{
			//TODO print the count of the number of entries in the filter view
			//    iTestStep.INFO_PRINTF1(_L("Filtered view is ready for use"));
			//  iInstrumentation.RaiseInstrumentationEventNotificationL(MTestInstrumentation::EPointContactsFilteringEnd);
			//iTestStep.INFO_PRINTF2(_L("Number of entries in the database which satisfy the filter criteria is %D"),iFilterView->CountL());
			iFilteredViewExists = ETrue;
			StartL();
			}
		}
	}

void CDbViewEngine::StartL()
	{
	if (iFilteredViewExists)
		{
		CActiveScheduler::Stop();
		TInt count = iFilterView->CountL();
		iObserver->Printf(_L("Expecting %d results returned for filter %d and got %d\n"),iExpectedContactMatch, iFilterType, count);
		if (count == iExpectedContactMatch)
			{
			iObserver->HandleTestResults(KErrNone);
			}
		else
			{
			iObserver->HandleTestResults(KErrNotFound);
			}

		}
	else
		{
		TRequestStatus *pS = &iStatus;
		User::RequestComplete(pS, KErrNone);
		SetActive();
		}
	}

void CDbViewEngine::SetFilterTypeL(const TInt aFilter)
	{
	iFilterType = aFilter;
	
	}

TInt CDbViewEngine::RunError(TInt aError)
	{
	return aError;
	}
