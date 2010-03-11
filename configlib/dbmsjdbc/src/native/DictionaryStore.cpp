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
#include "dbmsjni/com_symbian_store_DictionaryStore.h"
#include "DictionaryStore.h"
#include "Utils.h"

extern CTrapCleanup* gCleanup; // clean-up stack
extern TPanicHandler gPanicHandler;
extern jclass gExcCls;


// //
// EmbeddedStore class implementation

DictionaryStore::DictionaryStore() {
iStore = NULL;
}

DictionaryStore::~DictionaryStore() {
	if ( iStore != NULL ) {
		delete iStore;
		iStore = NULL;
	}
	iFs.Close();
}

DictionaryStore* DictionaryStore::CreateL(const TDesC& aFileName, TUid aUid3) {
	DictionaryStore* store = new (ELeave) DictionaryStore();
	CleanupStack::PushL(store);
	User::LeaveIfError(store->iFs.Connect());
	store->iStore = CDictionaryFileStore::OpenL(store->iFs, aFileName, aUid3);
	CleanupStack::Pop(store); 
	return store;
}

void DictionaryStore::Close() {
}

// //
// JNI implementations


/*
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _initNative
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStore__1initNative
  (JNIEnv * aEnv, jobject) {
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
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _create
 * Signature: (Ljava/lang/String;I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStore__1create
  (JNIEnv *aEnv, jobject, jstring aFileName, jint aUid) {
	  
	  RJString fname(*aEnv, aFileName);
	  TUid uid = TUid::Uid(aUid);
	  
	  DictionaryStore* store; 
	  TRAPD(error, store = DictionaryStore::CreateL(fname, uid));
	  
	  if(error != KErrNone) {
		  return error;
	  }
	  return (jint) store;
  }

/*
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _close
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_store_DictionaryStore__1close
  (JNIEnv *, jobject, jint aPeerHandle) {
		  DictionaryStore* store = (DictionaryStore*)aPeerHandle;
		  store->Close();
		  delete store;
  }

/*
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _commit
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStore__1commit
  (JNIEnv *, jobject, jint aPeerHandle) {
	  return ((DictionaryStore*)aPeerHandle)->iStore->Commit();
  }

/*
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _revert
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStore__1revert
  (JNIEnv *, jobject, jint aPeerHandle) {
	  DictionaryStore* store = (DictionaryStore*)aPeerHandle;
	  TRAPD(error, store->iStore->RevertL());
	  return error; 
  }
  
/*
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _remove
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStore__1remove
  (JNIEnv *, jobject, jint aPeerHandle, jint aUid){
	  DictionaryStore* store = (DictionaryStore*)aPeerHandle;
	  TUid uid = TUid::Uid(aUid);
	  TRAPD(error, store->iStore->RemoveL(uid));
	  return error; 
 
}

/*
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _isNull
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStore__1isNull
  (JNIEnv *, jobject, jint aPeerHandle) {
	  DictionaryStore* store = (DictionaryStore*)aPeerHandle;
	  TRAPD(error, store->iStore->IsNullL());
	  return error;
  }

/*
 * Class:     com_symbian_store_DictionaryStore
 * Method:    _isPresent
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_DictionaryStore__1isPresent
  (JNIEnv *, jobject, jint aPeerHandle, jint aUid) {
	  DictionaryStore* store = (DictionaryStore*)aPeerHandle;
	  TUid uid = TUid::Uid(aUid); 
	  TRAPD(error, store->iStore->IsPresentL(uid));
	  return error;
  }


