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
#include "dbmsjni/com_symbian_store_EmbeddedStoreInputStream.h"
#include "StoreInputStream.h"
#include "StreamStore.h"
#include "Utils.h"
#include "errortranslator.h"

//#define THROW_IOE_IF_ERROR(a,jni) if ( a != KErrNone ) {\
//	TBuf8<256> exception;\
//	TBuf8<256> message;\
//	GetException(a, exception, message);\
//	exception.Append('\0');\
//	message.Append('\0');\
//	ThrowExc(jni, exception, message);\
//	return a;\
//}
//
//#define THROW_IOE_IF_ERROR_STR(a,jni) if ( a != KErrNone ) {\
//	TBuf8<256> exception;\
//	TBuf8<256> message;\
//	GetException(a, exception, message);\
//	exception.Append('\0');\
//	message.Append('\0');\
//	ThrowExc(jni, exception, message);\
//	return NULL;\
//}

// //
// StoreInputStream class implementation


// //
// JNI implementations



/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _create
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_EmbeddedStoreInputStream__1create
  (JNIEnv *, jobject, jint aStorePeerHandle, jint aStrId) {
	StreamStore* streamStore = (StreamStore*)aStorePeerHandle;
	StoreInputStream* inStream = new StoreInputStream();
	RStoreReadStream* strptr = new RStoreReadStream();
	inStream->iInput = strptr;
	TStreamId id ( aStrId);
	TRAPD(error, strptr->OpenL(*(streamStore->iStore), id));
	if ( error < 0 ) {
		return error;
	}
	return (jint)inStream;
}


