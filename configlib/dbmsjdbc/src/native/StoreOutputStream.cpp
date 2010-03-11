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
#include "dbmsjni/com_symbian_store_StoreOutputStream.h"
#include "StoreOutputStream.h"
#include "Utils.h"


// //
// StoreOutputStream class implementation


// //
// JNI implementations

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _close
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_store_StoreOutputStream__1close
  (JNIEnv *, jobject, jint aPeerHandle) {
	StoreOutputStream* stream = (StoreOutputStream*)aPeerHandle;
	stream->iOutput->Close();
	delete stream->iOutput;
	delete stream;
}

//*
// * Class:     com_symbian_store_StoreOutputStream
// * Method:    _create
// * Signature: (I)I
// */
//JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1create__II
//  (JNIEnv *, jobject, jint aStorePeerHandle, jint aStreamId) {
//	StreamStore* streamStore = (StreamStore*)aStorePeerHandle;
//	StoreOutputStream* outStream = new StoreOutputStream();
//	outStream->iOutput = new RStoreWriteStream();
//	TStreamId id ( aStreamId);
//	TRAPD(error, outStream->iOutput->OpenL(*(streamStore->iStore), id));
//	if ( error == KErrNotFound ) {
//		TRAP(error, outStream->iOutput->OpenL(*(streamStore->iStore), id));
//	}
//	if ( error < 0 ) {
//		return error;
//	}
//	return (jint)outStream;
//}

//*
// * Class:     com_symbian_store_StoreOutputStream
// * Method:    _getStreamId
// * Signature: (I)I
// */
//JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1getStreamId
//  (JNIEnv *, jobject, jint aPeerHandle) {
//	StoreOutputStream* outStream = (StoreOutputStream*)aPeerHandle;
//	return outStream->iId;
//}

//*
// * Class:     com_symbian_store_StoreOutputStream
// * Method:    _create
// * Signature: (I)I
// */
//JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1create__I
//  (JNIEnv *, jobject, jint aStorePeerHandle) {
//	StreamStore* streamStore = (StreamStore*)aStorePeerHandle;
//	StoreOutputStream* outStream = new StoreOutputStream();
//	outStream->iOutput = new RStoreWriteStream();
//	TStreamId id;
//	TRAPD(error, id = outStream->iOutput->CreateL(*(streamStore->iStore)));
//	if ( error < 0 ) {
//		return error;
//	}
//	outStream->iId = id.Value();
//	return (jint)outStream;
//}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _flush
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1flush
  (JNIEnv *, jobject, jint aPeerHandle) {
	StoreOutputStream* stream = (StoreOutputStream*)aPeerHandle;
	TRAPD(error, stream->iOutput->CommitL());
	return error;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeBytes
 * Signature: (I[BII)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeBytes
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jbyteArray aBuffer, jint aFrom, jint aLen) {
	StoreOutputStream* stream = (StoreOutputStream*)aPeerHandle;
	jboolean isCopy = JNI_FALSE;
	// no copying needed
	jbyte* memptr = aEnv->GetByteArrayElements(aBuffer, &isCopy);
	memptr+=aFrom;
	TRAPD(err,stream->iOutput->WriteL((const TUint8*)memptr, aLen) );
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeDes8String
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeDes8String
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jstring aString) {
	StoreOutputStream* stream = (StoreOutputStream*)aPeerHandle;
	RJString str(*aEnv, aString);
	RBuf8 b;
	TRAPD(err, b.CreateL(str.Length()));
	if ( err != KErrNone ) {
		return err;
	}
	b.Copy(str);
	TRAP(err, stream->iOutput->WriteL(b));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeDes16
 * Signature: (I[SII)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeDes16__I_3SII
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jshortArray aArray, jint aFrom, jint aLen) {
	StoreOutputStream* stream = (StoreOutputStream*)aPeerHandle;
	jboolean isCopy = JNI_FALSE;
	jshort* shorts = aEnv->GetShortArrayElements(aArray, &isCopy);
	shorts+=aFrom;
	TRAPD(err, stream->iOutput->WriteL((const TUint16*)shorts,aLen));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeUInt16
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeUInt16
  (JNIEnv *, jobject, jint aPeerHandle, jint aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TUint16 value = (TUint16)(aValue & 0xFFFF);
	TRAPD(err,os->iOutput->WriteUint16L(value));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeDes16
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeDes16__ILjava_lang_String_2
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jstring aString) {
	StoreOutputStream* stream = (StoreOutputStream*)aPeerHandle;
	RJString str(*aEnv, aString);
	TRAPD(err, stream->iOutput->WriteL(str));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeUInt8
 * Signature: (IS)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeUInt8
  (JNIEnv *, jobject, jint aPeerHandle, jshort aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TUint8 value = (TUint8)(aValue & 0xFF);
	TRAPD(err,os->iOutput->WriteUint8L(value));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeReal32
 * Signature: (IF)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeReal32
  (JNIEnv *, jobject, jint aPeerHandle, jfloat aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TRAPD(err,os->iOutput->WriteReal32L(aValue));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeInt16
 * Signature: (IS)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeInt16
  (JNIEnv *, jobject, jint aPeerHandle, jshort aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TRAPD(err,os->iOutput->WriteInt16L(aValue));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeInt32
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeInt32
  (JNIEnv *, jobject, jint aPeerHandle, jint aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TRAPD(err,os->iOutput->WriteInt32L(aValue));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeInt8
 * Signature: (IB)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeInt8
  (JNIEnv *, jobject, jint aPeerHandle, jbyte aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TRAPD(err,os->iOutput->WriteInt8L(aValue));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeReal64
 * Signature: (ID)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeReal64
  (JNIEnv *, jobject, jint aPeerHandle, jdouble aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TRAPD(err,os->iOutput->WriteReal64L(aValue));
	return err;
}


/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeUInt32
 * Signature: (IJ)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeUInt32
  (JNIEnv *, jobject, jint aPeerHandle, jlong aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TUint32 value = (TUint32)(aValue & 0xFFFFFFFFL);
	TRAPD(err,os->iOutput->WriteUint32L(value));
	return err;
}

void doWriteCardinalityL(JNIEnv *, jobject, jint aPeerHandle, TInt aVal) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	RWriteStream& str = *(os->iOutput);
	str<<TCardinality(aVal);
}
/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeCardinality
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeCardinality
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aValue) {
	TRAPD(err,doWriteCardinalityL(aEnv, NULL, aPeerHandle, aValue));
	return err;
}

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeBuf16
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeBuf16
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jstring aString) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	RWriteStream& stream = *(os->iOutput);
	RJString str(*aEnv, aString);
	TRAPD(err, ExternalizeL(str, stream));
	return err;
}

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeBuf8
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeBuf8__ILjava_lang_String_2
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jstring aString) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	RWriteStream& stream = *(os->iOutput);
	RJString str(*aEnv, aString);
	RBuf8 buf;
	TRAPD(err, buf.CreateL(str.Length()));
	if ( err != KErrNone ) {
		return err;
	}
	buf.Copy(str);
	TRAP(err, ExternalizeL(buf, stream));
	return err;
}

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeBuf8
 * Signature: (I[B)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeBuf8__I_3B
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jbyteArray aData) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	RWriteStream& stream = *(os->iOutput);
	jboolean isCopy = JNI_FALSE;
	// no copying needed
	jbyte* memptr = aEnv->GetByteArrayElements(aData, &isCopy);
	int len = aEnv->GetArrayLength(aData);
	RBuf8 buf;
	TRAPD(err, buf.CreateL(len));
	if ( err != KErrNone ) {
		return err;
	}
	buf.Append((TUint8 *)memptr, len);
	TRAP(err, ExternalizeL(buf, stream));
	if ( err != KErrNone ) {
		return err;
	}
	buf.Close();
	return err;
}

void doWriteInt64L(RWriteStream& stream, TInt64 value) {
	stream << value;
}

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeInt64
 * Signature: (IJ)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeInt64
  (JNIEnv *, jobject, jint aPeerHandle, jlong aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TInt64 value = (TInt64)(aValue);
	RWriteStream& stream = *(os->iOutput);
	TRAPD(err, doWriteInt64L(stream, value) );
	return err;
}

/*
 * Class:     com_symbian_store_StoreOutputStream
 * Method:    _writeUInt64
 * Signature: (IJ)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_store_StoreOutputStream__1writeUInt64
	(JNIEnv *, jobject, jint aPeerHandle, jlong aValue) {
	StoreOutputStream* os = (StoreOutputStream*)aPeerHandle;
	TInt64 value = (TUint64)(aValue);
	RWriteStream& stream = *(os->iOutput);
	TRAPD(err, doWriteInt64L(stream, value));
	return err;
}

