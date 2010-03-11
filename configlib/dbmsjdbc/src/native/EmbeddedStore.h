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

#ifndef __EmbeddedStore_h__
#define __EmbeddedStore_h__
#include <e32std.h>
#include <s32stor.h>
#include "StreamStore.h"
#include <s32mem.h>

class EmbeddedStore : public StreamStore {

public:
	CBufFlat* iContent;
	RBufWriteStream* iOutstream;
	RBufReadStream* iInstream;

public:
	static EmbeddedStore* CreateL();
	static EmbeddedStore* CreateL(const TUint8* content, int length);
	EmbeddedStore();
	~EmbeddedStore();
	void Close();
};

#endif
