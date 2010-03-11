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

#ifndef VIEWENGINE_H
#define VIEWENGINE_H

#include <e32base.h>	// For CActive, link against: euser.lib
#include <e32std.h>		// For RTimer, link against: euser.lib
#include <cntdb.h>
#include <cntitem.h>
#include <cntfldst.h>
#include <cntview.h>
#include <cntviewbase.h>
#include <MTestCaseObserver.h>
#include "SdbTestFramework.h"

_LIT(KRemoteViewName, "RemoteView");

class CDbViewEngine : public CActive, public MContactViewObserver
	{
public:
	// Cancel and destroy
	~CDbViewEngine();

	// Two-phased constructor.
	static CDbViewEngine* NewL(RSdbTest* aObserver, const TInt aFilter, TInt aReturnCount);

	// Two-phased constructor.
	static CDbViewEngine* NewLC(RSdbTest* aObserver, const TInt aFilter, TInt aReturnCount);
	
	void HandleContactViewEvent(const CContactViewBase& aView, const TContactViewEvent& aEvent);

public:
	// New functions
	// Function for making the initial request
	void StartL();

private:
	// C++ constructor
	CDbViewEngine(RSdbTest* aObserver);

	// Second-phase constructor
	void ConstructL(const TInt aFilter, TInt aReturnCount);

private:
	// From CActive
	// Handle completion
	void RunL();

	// How to cancel me
	void DoCancel();

	// Override to handle leaves from RunL(). Default implementation causes
	// the active scheduler to panic.
	TInt RunError(TInt aError);
	
	/**
	 * Set filter type for filtered view on contacts database
	 * @param aFilter one of filter string e.g. customfilter1, customfilter2 
	 */
	void SetFilterTypeL(const TInt aFilter);
	
	CContactDatabase* CDbViewEngine::OpenDefaultDbL();

private:
	enum TViewEngineState
		{
		EUninitialized, // Uninitialized
		EInitialized, // Initalized
		EError
		// Error condition
		};

private:
	RSdbTest* iObserver;
	
	RContactViewSortOrder iSortOrder_1;
	
	CContactDatabase* iDb;
	CContactNamedRemoteView* iNamedRemoteView;
	CContactFilteredView* iFilterView;
	
	TInt iNamedRemoteViewExists;
	TBool iFilteredViewExists;
	TInt iState;
	TInt iFilterType;
	TInt iExpectedContactMatch;


	};

#endif // VIEWENGINE_H
