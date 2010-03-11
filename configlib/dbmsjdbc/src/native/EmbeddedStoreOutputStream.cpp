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
// EmbeddedStoreInputStream.h
// 
//

#include <jni.h>
#include "dbmsjni/com_symbian_store_EmbeddedStoreOutputStream.h"
#include "StoreOutputStream.h"
#include "StreamStore.h"
#include "Utils.h"


// //
// StoreOutputStream class implementation


// //
// JNI implementations


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _create
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStoreOutputStream__1create__II
  (JNIEnv *, jobject, jint aStorePeerHandle, jint aStreamId) {
	StreamStore* streamStore = (StreamStore*)aStorePeerHandle;
	StoreOutputStream* outStream = new StoreOutputStream();
	RStoreWriteStream* strptr = new RStoreWriteStream();
	outStream->iOutput = strptr;
	TStreamId id ( aStreamId);
	TRAPD(error, strptr->OpenL(*(streamStore->iStore), id));
	if ( error == KErrNotFound ) {
		TRAP(error, strptr->OpenL(*(streamStore->iStore), id));
	}
	if ( error < 0 ) {
		return error;
	}
	return (jint)outStream;
}

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _create
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStoreOutputStream__1create__I
  (JNIEnv *, jobject, jint aStorePeerHandle) {
	StreamStore* streamStore = (StreamStore*)aStorePeerHandle;
	StoreOutputStream* outStream = new StoreOutputStream();
	RStoreWriteStream* strptr = new RStoreWriteStream();
	outStream->iOutput = strptr;
	CEmbeddedStore* embstore = (CEmbeddedStore*)streamStore->iStore;
	TStreamId id;
	TRAPD(error, id = strptr->CreateL(*embstore));
	if ( error < 0 ) {
		return error;
	}
	outStream->iId = id.Value();
	return (jint)outStream;
}

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _getStreamId
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStoreOutputStream__1getStreamId
  (JNIEnv *, jobject, jint aPeerHandle) {
	StoreOutputStream* outStream = (StoreOutputStream*)aPeerHandle;
	return outStream->iId;
}


