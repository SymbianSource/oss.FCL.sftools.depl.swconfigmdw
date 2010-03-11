// Copyright (c) 1998-2009 Nokia Corporation and/or its subsidiary(-ies).
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

#ifndef __DictionaryStore_h__
#define __DictionaryStore_h__
#include <e32std.h>
#include <s32stor.h>
#include <s32file.h>
#include <s32mem.h>
#include <e32cmn.h>

class DictionaryStore  {

public:
	CDictionaryFileStore* iStore;
	RFs iFs;

public:
	static DictionaryStore* CreateL(const TDesC& aFileName, TUid aUid3);
	DictionaryStore();
	~DictionaryStore();
	void Close();
};

#endif
