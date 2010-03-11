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

#ifndef __DbmsResultSet_h__
#define __DbmsResultSet_h__
#include <e32std.h>
#include <d32dbms.h>
#include "DbmsStatement.h"


class DbmsResultSet {

public:
	DbmsStatement* iStatement;
	
public:
	DbmsResultSet(DbmsStatement* aStatement);
	~DbmsResultSet();
	
};

#endif
