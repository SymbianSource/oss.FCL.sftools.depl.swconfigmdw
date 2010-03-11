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
#include "dbmsjni/com_symbian_store_EmbeddedStore.h"
#include "EmbeddedStore.h"



// //
// EmbeddedStore class implementation

EmbeddedStore::EmbeddedStore() {
	iStore = NULL;
	iInstream = NULL;
	iOutstream = NULL;
	iContent = NULL;
}

EmbeddedStore::~EmbeddedStore() {
	if ( iStore != NULL ) {
		delete iStore;
		iStore = NULL;
	}
	if ( iInstream != NULL ) {
		delete iInstream;
		iInstream = NULL;
	}
	if ( iOutstream != NULL ) {
		delete iOutstream;
		iOutstream = NULL;
	}
	if ( iContent != NULL ) {
		delete iContent;
		iContent = NULL;
	}
}

EmbeddedStore* EmbeddedStore::CreateL(const TUint8* content, int length) {
	EmbeddedStore* store = new (ELeave) EmbeddedStore();
	store->iContent = CBufFlat::NewL(length);
	RBufWriteStream tmpout(*(store->iContent));
	CleanupClosePushL(tmpout);
	tmpout.WriteL(content, length);
	tmpout.CommitL();
	tmpout.Close();
	store->iInstream = new RBufReadStream(*(store->iContent));
	store->iStore = CEmbeddedStore::FromL(*(store->iInstream));
	CleanupStack::Pop(1);
	return store;
}

EmbeddedStore* EmbeddedStore::CreateL(){
	EmbeddedStore* store = new (ELeave) EmbeddedStore();
	store->iContent = CBufFlat::NewL(4096);
	store->iOutstream = new RBufWriteStream(*(store->iContent));
	store->iStore = CEmbeddedStore::NewL(*(store->iOutstream));
	return store;
}

void EmbeddedStore::Close() {
	if ( iStore != NULL ) {
		CEmbeddedStore* store = (CEmbeddedStore*)iStore;
		store->Commit();
		store->Detach();
	}
	if ( iOutstream != NULL ) {
		TRAPD(error, iOutstream->CommitL());
		iOutstream->Close();
	}
	if ( iInstream != NULL ) {
		iInstream->Close();
	}
}

// //
// JNI implementations


JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStore__1create__
  (JNIEnv *aEnv, jobject){
	EmbeddedStore* store;
	TRAPD(error, store = EmbeddedStore::CreateL());
	if ( error < KErrNone ) {
		return error;
	}
	return (jint)store;
}

/*
 * Class:     com_symbian_store_EmbeddedStore
 * Method:    _setRoot
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStore__1setRoot
  (JNIEnv *, jobject, jint aPeerHandle, jint aId) {
	EmbeddedStore* store = (EmbeddedStore*)aPeerHandle;
	TStreamId id(aId);
	CEmbeddedStore* es = (CEmbeddedStore*)(store->iStore);
	TRAPD(error, es->SetRootL(id));
	return error;
}

/*
 * Class:     com_symbian_store_EmbeddedStore
 * Method:    _root
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStore__1root
  (JNIEnv *, jobject, jint aPeerHandle) {
	EmbeddedStore* store = (EmbeddedStore*)aPeerHandle;
	TStreamId id = ((CEmbeddedStore*)(store->iStore))->Root();
	return id.Value();
}

/*
 * Class:     com_symbian_store_EmbeddedStore
 * Method:    _create
 * Signature: ([B)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStore__1create___3B
  (JNIEnv *aEnv, jobject, jbyteArray aData) {
	jbyte* buf = aEnv->GetByteArrayElements(aData, NULL);
	jint len = aEnv->GetArrayLength(aData);
	EmbeddedStore* store;
	TRAPD(error, store = EmbeddedStore::CreateL((const TUint8*)buf, len));
	if ( error < KErrNone ) {
		return error;
	}
	return (jint)store;
}

/*
 * Class:     com_symbian_store_EmbeddedStore
 * Method:    _close
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStore__1close
  (JNIEnv *, jobject, jint aPeerHandle) {
	EmbeddedStore* store = (EmbeddedStore*)aPeerHandle;
	store->Close();
	delete store;
	return KErrNone;
}

/*
 * Class:     com_symbian_store_EmbeddedStore
 * Method:    _getContent
 * Signature: (I[B)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStore__1getContent
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jbyteArray aBuffer) {
	EmbeddedStore* store = (EmbeddedStore*)aPeerHandle;
	jint len = store->iContent->Size();
	jint arraylen = aEnv->GetArrayLength(aBuffer);
	if ( len > arraylen ) {
		return KErrNoMemory;
	}
	TPtr8 ptr(store->iContent->Ptr(0));
	aEnv->SetByteArrayRegion(aBuffer, 0, len, (const jbyte*)(ptr.Ptr()));
	return len;
}

/*
 * Class:     com_symbian_store_EmbeddedStore
 * Method:    _getContentSize
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStore__1getContentSize
  (JNIEnv *, jobject, jint aPeerHandle) {
	EmbeddedStore* store = (EmbeddedStore*)aPeerHandle;
	return store->iContent->Size();
}
