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
#include "dbmsjni/com_symbian_store_StreamStore.h"
#include "StreamStore.h"
#include "Utils.h"
#include <s32stor.h>
#include <errortranslator.h>

extern CTrapCleanup* gCleanup; // clean-up stack
extern TPanicHandler gPanicHandler;
extern jclass gExcCls;

// //
// StreamStore class implementation

// nothing to implement

// //
// JNI implementations

JNIEXPORT jint JNICALL Java_com_symbian_store_StreamStore__1initNative
  (JNIEnv *aEnv, jobject) {
	if ( gCleanup == NULL ) {
		// init globals
		gCleanup=CTrapCleanup::New(); // get clean-up stack
		gPanicHandler = &SosPanicHandler;
		jclass excCls = aEnv->FindClass("java/lang/RuntimeException");
		if ( excCls == NULL )
			{
			printf("Could not create exception class java/lang/RuntimeException in DbmsConnection::init ...\n");
			return KErrGeneral;
			}
		else
			{
			gExcCls = (jclass)(aEnv->NewGlobalRef(excCls));
			if ( gExcCls == NULL )
				{
				printf("Could not create glref to exception class java/lang/RuntimeException in DbmsConnection::init ...\n");
				return KErrGeneral;
				}
			}
	}
	return KErrNone;
}

/*
 * Class:     com_symbian_store_StreamStore
 * Method:    _delete
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StreamStore__1delete
  (JNIEnv *, jobject, jint aPeerHandle, jint aStreamId) {
	TStreamId strid(aStreamId);
	StreamStore* store = (StreamStore*) aPeerHandle;
	TRAPD(error, store->iStore->DeleteL(strid));
	return error;
}

/*
 * Class:     com_symbian_store_StreamStore
 * Method:    _compact
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StreamStore__1compact
  (JNIEnv *, jobject, jint aPeerHandle) {
	StreamStore* store = (StreamStore*) aPeerHandle;
	TRAPD(error, store->iStore->CompactL());
	return error;
}

/*
 * Class:     com_symbian_store_StreamStore
 * Method:    _extend
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StreamStore__1extend
  (JNIEnv *, jobject, jint aPeerHandle) {
	StreamStore* store = (StreamStore*) aPeerHandle;
	TInt strid;
	TRAPD(error, strid = (store->iStore->ExtendL()).Value());
	if ( error < KErrNone ) {
		return error;
	}
	return strid;
}

/*
 * Class:     com_symbian_store_StreamStore
 * Method:    _reclaim
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StreamStore__1reclaim
  (JNIEnv *, jobject, jint aPeerHandle) {
	StreamStore* store = (StreamStore*) aPeerHandle;
	TRAPD(error, store->iStore->ReclaimL());
	return error;
}

/*
 * Class:     com_symbian_store_StreamStore
 * Method:    _commit
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StreamStore__1commit
  (JNIEnv *, jobject, jint aPeerHandle) {
	StreamStore* store = (StreamStore*) aPeerHandle;
	TRAPD(error, store->iStore->CommitL());
	return error;
}

/*
 * Class:     com_symbian_store_StreamStore
 * Method:    _revert
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StreamStore__1revert
  (JNIEnv *, jobject, jint aPeerHandle) {
	StreamStore* store = (StreamStore*) aPeerHandle;
	TRAPD(error, store->iStore->RevertL());
	return error;
}

JNIEXPORT jstring JNICALL Java_com_symbian_store_StreamStore__1translateNativeError
  (JNIEnv *aEnv, jclass, jint aErrorCode) {
	TBuf8<256> buf;
	TranslateError(aErrorCode, buf);
	TBuf<256> buf16;
	buf16.Copy(buf);
	jstring jstr = CreateJavaString(aEnv, buf16);
	return jstr;
}

