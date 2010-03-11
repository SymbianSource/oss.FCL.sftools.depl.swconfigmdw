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

#ifndef __DbmsStatement_h__
#define __DbmsStatement_h__
#include <e32std.h>
#include <d32dbms.h>
#include "DbmsConnection.h"


class DbmsStatement {

public:
	DbmsConnection* iConnection;
	RDbView 		iView;
	
public:
	DbmsStatement(DbmsConnection* aConnection);
	~DbmsStatement();
	void Close();
};

#endif
