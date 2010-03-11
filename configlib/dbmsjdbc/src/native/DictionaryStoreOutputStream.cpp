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
#include "dbmsjni/com_symbian_store_DictionaryStoreOutputStream.h"
#include "StoreOutputStream.h"
#include "DictionaryStore.h"
#include "Utils.h"

/*
 * Class:     com_symbian_store_DictionaryStoreOutputStream
 * Method:    _create
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStoreOutputStream__1create
  (JNIEnv *, jobject, jint aStorePeerHandle, jint aUid) {
	DictionaryStore* store = (DictionaryStore*)aStorePeerHandle;
	StoreOutputStream* outStream = new StoreOutputStream();
	RDictionaryWriteStream* strptr = new RDictionaryWriteStream();
	outStream->iOutput = strptr;
	TUid uid  = TUid::Uid(aUid);
	TRAPD(error, strptr->AssignL(*(store->iStore), uid));
	if ( error != KErrNone ) {
		return error;
	}
	outStream->iId = aUid;
	return (jint)outStream;
}
