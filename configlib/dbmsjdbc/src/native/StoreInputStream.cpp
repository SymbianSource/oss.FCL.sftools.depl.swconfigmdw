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
#include "dbmsjni/com_symbian_store_StoreInputStream.h"
#include "StoreInputStream.h"
#include "Utils.h"
#include "errortranslator.h"

#define THROW_IOE_IF_ERROR(a,jni) if ( a != KErrNone ) {\
	TBuf8<256> exception;\
	TBuf8<256> message;\
	GetException(a, exception, message);\
	exception.Append('\0');\
	message.Append('\0');\
	ThrowExc(jni, exception, message);\
	return a;\
}

#define THROW_IOE_IF_ERROR_STR(a,jni) if ( a != KErrNone ) {\
	TBuf8<256> exception;\
	TBuf8<256> message;\
	GetException(a, exception, message);\
	exception.Append('\0');\
	message.Append('\0');\
	ThrowExc(jni, exception, message);\
	return NULL;\
}

// //
// StoreInputStream class implementation


// //
// JNI implementations


JNIEXPORT void JNICALL Java_com_symbian_store_StoreInputStream__1close
  (JNIEnv *, jobject, jint aPeerHandle) {
	StoreInputStream* stream = (StoreInputStream*)aPeerHandle;
	stream->iInput->Close();
	delete stream->iInput;
	delete stream;
}

//*
// * Class:     com_symbian_store_StoreInputStream
// * Method:    _create
// * Signature: (I)I
// */
//JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1create
//  (JNIEnv *, jobject, jint aStorePeerHandle, jint aStrId) {
//	StreamStore* streamStore = (StreamStore*)aStorePeerHandle;
//	StoreInputStream* inStream = new StoreInputStream();
//	inStream->iInput = new RStoreReadStream();
//	TStreamId id ( aStrId);
//	TRAPD(error, inStream->iInput->OpenL(*(streamStore->iStore), id));
//	if ( error < 0 ) {
//		return error;
//	}
//	return (jint)inStream;
//}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readByte
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readByte
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jint result = 0;
	TRAPD(err, result = os->iInput->ReadInt8L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readBytes
 * Signature: (I[BII)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readBytes
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jbyteArray aBuffer, jint aFrom, jint aLen) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf8 buf;
	TRAPD(err, buf.CreateL(aLen));
	THROW_IOE_IF_ERROR(err, aEnv);
	TRAP(err, os->iInput->ReadL(buf));
	THROW_IOE_IF_ERROR(err, aEnv);
	aEnv->SetByteArrayRegion(aBuffer, aFrom, aLen, (jbyte*)(buf.Ptr()));
	buf.Close();
	return aLen;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readInt16
 * Signature: (I)S
 */
JNIEXPORT jshort JNICALL Java_com_symbian_store_StoreInputStream__1readInt16
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jshort result = 0;
	TRAPD(err, result = os->iInput->ReadInt16L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readInt32
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readInt32
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jint result = 0;
	TRAPD(err, result = os->iInput->ReadInt32L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
}

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readInt8
 * Signature: (I)B
 */
JNIEXPORT jbyte JNICALL Java_com_symbian_store_StoreInputStream__1readInt8
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jbyte result = 0;
	TRAPD(err, result = os->iInput->ReadInt8L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
  }
/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readReal32
 * Signature: (I)F
 */
JNIEXPORT jfloat JNICALL Java_com_symbian_store_StoreInputStream__1readReal32
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jfloat result = 0;
	TRAPD(err, result = os->iInput->ReadReal32L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
  }

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readReal64
 * Signature: (I)D
 */
JNIEXPORT jdouble JNICALL Java_com_symbian_store_StoreInputStream__1readReal64
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jdouble result = 0;
	TRAPD(err, result = os->iInput->ReadReal64L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
  }

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readUInt32
 * Signature: (I)J
 */
JNIEXPORT jlong JNICALL Java_com_symbian_store_StoreInputStream__1readUInt32
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jlong result = 0;
	TRAPD(err, result = os->iInput->ReadUint32L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readUInt16
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readUInt16
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jint result = 0;
	TRAPD(err, result = os->iInput->ReadUint16L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readUInt8
 * Signature: (I)S
 */
JNIEXPORT jshort JNICALL Java_com_symbian_store_StoreInputStream__1readUInt8
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	jshort result = 0;
	TRAPD(err, result = os->iInput->ReadUint8L());
	THROW_IOE_IF_ERROR(err, aEnv);
	return result;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readDes16
 * Signature: (II)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_store_StoreInputStream__1readDes16__II
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aLen) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf16 buf;
	TRAPD(err, buf.CreateL(aLen));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TRAP(err, os->iInput->ReadL(buf, aLen));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	jstring string = CreateJavaString(aEnv, buf);
	buf.Close();
	return string;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readDes16
 * Signature: (I[SI)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readDes16__I_3SI
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jshortArray aBuffer, jint aLen) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf16 buf;
	TRAPD(err, buf.CreateL(aLen));
	THROW_IOE_IF_ERROR(err, aEnv);
	TRAP(err, os->iInput->ReadL(buf));
	THROW_IOE_IF_ERROR(err, aEnv);
	aEnv->SetShortArrayRegion(aBuffer, 0, aLen, (jshort*)(buf.Ptr()));
	buf.Close();
	return aLen;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readDes16
 * Signature: (IC)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_store_StoreInputStream__1readDes16__IC
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jchar aDelimiter) {
	THROW_IOE_IF_ERROR_STR(KErrNotSupported, aEnv);
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readDes16
 * Signature: (I[SC)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readDes16__I_3SC
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jshortArray aArray, jchar aDelimiter) {
	THROW_IOE_IF_ERROR(KErrNotSupported, aEnv);
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readDes8
 * Signature: (I[BC)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readDes8
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jbyteArray aArray, jchar aDelimiter) {
	THROW_IOE_IF_ERROR(KErrNotSupported, aEnv);
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readDes8String
 * Signature: (IC)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_store_StoreInputStream__1readDes8String__IC
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jchar aDelimiter) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf16 buf;
	RBuf8 buf8;
	TInt mxlen = 8192;
	TRAPD(err, buf.CreateL(mxlen));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TRAP(err, buf8.CreateL(mxlen));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TChar ch(aDelimiter);
	TRAP(err, os->iInput->ReadL(buf8, ch));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	buf.Copy(buf8);
	jstring string = CreateJavaString(aEnv, buf);
	buf.Close();
	buf8.Close();
	return string;
}


/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readDes8String
 * Signature: (II)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_store_StoreInputStream__1readDes8String__II
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aLen) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf16 buf;
	RBuf8 buf8;
	TRAPD(err, buf.CreateL(aLen));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TRAP(err, buf8.CreateL(aLen));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TRAP(err, os->iInput->ReadL(buf8));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	buf.Copy(buf8);
	jstring string = CreateJavaString(aEnv, buf);
	buf.Close();
	buf8.Close();
	return string;
}


void doReadCardinalityL(JNIEnv *aEnv, jobject, jint aPeerHandle, TCardinality& card) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	(*(os->iInput))>>card;
}

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readCardinality
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreInputStream__1readCardinality
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	TCardinality card;
	TRAPD(err, doReadCardinalityL(aEnv, NULL, aPeerHandle, card));
	THROW_IOE_IF_ERROR(err, aEnv);
	return card;
}

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readBuf8
 * Signature: (I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_store_StoreInputStream__1readBuf8
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aMaxSize) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf8 buf;
	TRAPD(err, buf.CreateL(aMaxSize));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TRAP(err, InternalizeL(buf, *(os->iInput)) );
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	RBuf buf16;
	TRAP(err, buf16.CreateL(aMaxSize));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	buf16.Copy(buf);
	jstring string = CreateJavaString(aEnv, buf16);
	buf.Close();
	buf16.Close();
	return string;
}

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readBuf16
 * Signature: (I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_store_StoreInputStream__1readBuf16
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aMaxSize) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf16 buf;
	TRAPD(err, buf.CreateL(aMaxSize));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TRAP(err, InternalizeL(buf, *(os->iInput)) );
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	jstring string = CreateJavaString(aEnv, buf);
	buf.Close();
	return string;
}

JNIEXPORT jbyteArray JNICALL Java_com_symbian_store_StoreInputStream__1readBuf8Raw
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aMaxSize) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	RBuf8 buf;
	TRAPD(err, buf.CreateL(aMaxSize));
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	TRAP(err, InternalizeL(buf, *(os->iInput)) );
	THROW_IOE_IF_ERROR_STR(err, aEnv);
	jbyteArray buffer = aEnv->NewByteArray(buf.Length());
	aEnv->SetByteArrayRegion(buffer, 0, buf.Length(), (jbyte *)(buf.Ptr()));
	buf.Close();
	return buffer;
}

void doReadInt64L(JNIEnv *aEnv, jobject, jint aPeerHandle, TInt64& value) {
	StoreInputStream* os = (StoreInputStream*)aPeerHandle;
	(*(os->iInput))>>value;
}

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readInt64
 * Signature: (I)J
 */
JNIEXPORT jlong JNICALL Java_com_symbian_store_StoreInputStream__1readInt64
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	TInt64 value;
	TRAPD(err, doReadInt64L(aEnv, NULL, aPeerHandle, value));
	THROW_IOE_IF_ERROR(err, aEnv);
	return (jlong)value;
}

/*
 * Class:     com_symbian_store_StoreInputStream
 * Method:    _readUInt64
 * Signature: (I)J
 */
JNIEXPORT jlong JNICALL Java_com_symbian_store_StoreInputStream__1readUInt64
  (JNIEnv *aEnv, jobject, jint aPeerHandle) {
	// cant read TUint64 as that is not supported by stream. Must read Int64 instead
	TInt64 value;
	TRAPD(err, doReadInt64L(aEnv, NULL, aPeerHandle, value));
	THROW_IOE_IF_ERROR(err, aEnv);
	return (jlong)value;
}

