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

#include <jni.h>
#include <stdio.h>
#include "dbmsjni/com_symbian_store_DictionaryStoreInputStream.h"
#include "StoreInputStream.h"
#include "DictionaryStore.h"
#include "Utils.h"
#include "errortranslator.h"

JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStoreInputStream__1create
  (JNIEnv *, jobject, jint aStorePeerHandle, jint aUid) {
	DictionaryStore * store = (DictionaryStore*)aStorePeerHandle;
	StoreInputStream* inStream = new StoreInputStream();
	RDictionaryReadStream* strptr = new RDictionaryReadStream();
	inStream->iInput = strptr;
	TUid uid = TUid::Uid(aUid);
	TRAPD(error, strptr->OpenL(*(store->iStore), uid));
	if ( error < 0 ) {
		return error;
	}
	return (jint)inStream;
}
