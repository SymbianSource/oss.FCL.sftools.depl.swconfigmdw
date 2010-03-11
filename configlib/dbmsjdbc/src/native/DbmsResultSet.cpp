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
#include "DbmsResultSet.h"
#include "DbmsStatement.h"
#include "DbmsConnection.h"
#include "Utils.h"
#include "dbmsjni/com_symbian_dbms_jdbc_DbmsResultSet.h"


// //
// DbmsResultSet peer
// //

DbmsResultSet::DbmsResultSet(DbmsStatement* aStatement){
	iStatement = aStatement;
}

DbmsResultSet::~DbmsResultSet(){
}


// //
// JNI
// //

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _rowcount
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1rowcount
  (JNIEnv *, jobject, jint aPeerHandle) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	jint res = 0;
	TRAPD(err, res = view.CountL() );
	if ( err != KErrNone ) {
		return err;
	}
	return res;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _colcount
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1colcount
  (JNIEnv *, jobject, jint aPeerHandle) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	return view.ColCount();
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _next
 * Signature: (II)Z
 */
JNIEXPORT jboolean JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1next
  (JNIEnv *, jobject, jint aPeerHandle, jint aCount) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TBool res = EFalse;
	TInt err = 0;
	for ( TInt i = 0; i < aCount ; i++ )
		{
		TRAP( err, res = view.NextL() );
		if ( err != KErrNone || ! res )
			{
			return false;
			}
		}
	TRAP(err, view.GetL());
	if ( err != KErrNone ) {
		return false;
	}
	return true;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _first
 * Signature: (I)Z
 */
JNIEXPORT jboolean JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1first
  (JNIEnv *, jobject, jint aPeerHandle){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TBool res = EFalse;
	TInt err = 0;
	TRAP(err, res = view.FirstL());
	if ( err != KErrNone ) {
		return false;
	}
	if ( res ) {
		TRAP(err, view.GetL());
		if ( err != KErrNone ) {
			return false;
		}
		return true;
	}
	return false;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _last
 * Signature: (I)Z
 */
JNIEXPORT jboolean JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1last
  (JNIEnv *, jobject, jint aPeerHandle) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TBool res = EFalse;
	TInt err = 0;
	TRAP(err, res = view.LastL());
	if ( res ) {
		TRAP(err, view.GetL());
		if ( err != KErrNone ) {
			return false;
		}
		return true;
	}
	return false;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _prev
 * Signature: (II)Z
 */
JNIEXPORT jboolean JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1prev
  (JNIEnv *, jobject, jint aPeerHandle, jint aCount) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TBool res = EFalse;
	TInt err = 0;
	for ( TInt i = 0; i < aCount ; i++ )
		{
		TRAP( err, res = view.PreviousL() );
		if ( err != KErrNone || ! res )
			{
			return false;
			}
		}
	TRAP(err, view.GetL());
	if ( err != KErrNone ) {
		return false;
	}
	return true;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _close
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1close
  (JNIEnv *, jobject, jint aPeerHandle) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	view.Close();
	delete rset;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    delete
 * Signature: (I)Z
 */
JNIEXPORT jboolean JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1delete
  (JNIEnv *, jobject, jint /*aPeerHandle*/) {
	// not implemented
	return false;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _isSigned
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1isSigned
  (JNIEnv *, jobject, jint aPeerHandle, jint aColNo) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TDbColType type = view.ColType(aColNo);
	switch ( type ) {
	case EDbColInt8  :
	case EDbColInt16 :
	case EDbColInt32 :
	case EDbColInt64 :
	case EDbColReal32:
	case EDbColReal64:
	{
		return 1;
	}break;
	default:
		return 0;
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _isFirst
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1isFirst
  (JNIEnv *, jobject, jint aPeerHandle) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	return view.AtBeginning();
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _isLast
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1isLast
  (JNIEnv *, jobject, jint aPeerHandle){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	return view.AtEnd();
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _isAutoIncrement
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1isAutoIncrement
  (JNIEnv *, jobject, jint aPeerHandle, jint aColumn) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TDbCol col = view.ColDef(aColumn);
	if ( col.iAttributes & TDbCol::EAutoIncrement ) {
		return 1; // Auto increment
	} else {
		return 0; // Not auto increment
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _isNullable
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1isNullable
  (JNIEnv *, jobject, jint aPeerHandle, jint aColumn) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TDbCol col = view.ColDef(aColumn);
	if ( col.iAttributes & TDbCol::ENotNull ) {
		return 1; // Nullable
	} else {
		return 0; // Not nullable
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _columnNames
 * Signature: (I[Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1columnNames
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jobjectArray aNames) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TInt colCount = view.ColCount();
    for( TInt i = 0 ; i < colCount ; i++ ) {
    	TDbCol col = view.ColDef(i+1);
    	jstring colName = CreateJavaString(aEnv,col.iName);
        aEnv->SetObjectArrayElement(aNames, i, colName);
    }
    return 0;
}


/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _coltypes
 * Signature: (I[I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1columnTypes
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jintArray aTypes) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TInt colCount = view.ColCount();
    for( TInt i = 0 ; i < colCount ; i++ ) {
    	TDbCol col = view.ColDef(i+1);
    	jint colType = col.iType;
        aEnv->SetIntArrayRegion(aTypes,i,1,&colType);
    }
    return 0;
}


/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getBoolean
 * Signature: (I)Z
 */
JNIEXPORT jboolean JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getBoolean
  (JNIEnv *, jobject, jint aPeerHandle, jint aColIndex) {
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TInt val = view.ColUint8(aColIndex);
	if ( val == 0 ) {
		return false;
	} else {
		return true;
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getByte
 * Signature: (I)B
 */
JNIEXPORT jbyte JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getByte
  (JNIEnv *, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	jbyte ret = view.ColInt8(aColIndex);
	return ret;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getShort
 * Signature: (I)S
 */
JNIEXPORT jshort JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getShort
  (JNIEnv *, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	return (jshort) view.ColInt16(aColIndex);
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getInteger
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getInteger
  (JNIEnv *, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TInt res = view.ColInt(aColIndex);
	return (jint)res;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getLong
 * Signature: (I)J
 */
JNIEXPORT jlong JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getLong
  (JNIEnv *, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	return (jlong) view.ColInt64(aColIndex);
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getFloat
 * Signature: (I)F
 */
JNIEXPORT jfloat JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getFloat
  (JNIEnv *, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	return (jfloat) view.ColReal32(aColIndex);
}


/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getTime
 * Signature: (I)J
 */
JNIEXPORT jlong JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getTime
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	TTime stored = view.ColTime(aColIndex);
	TInt64 time = stored.Int64();
	// sym time (0AD) to java time (1970AD) adjustment
	TInt64 adjustment = MAKE_TINT64(0x00dcddb3,0x0f2f8000);
	TInt64 result = time - adjustment;
	jlong rv = result / 1000;	// convert microseconds into millisconds
	return rv;
}


/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getText
 * Signature: (I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getText
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	jstring jstr = NULL;
	// handle wide/8bit text types
	TDbColNo colNo(aColIndex);
	if ( view.IsColNull(colNo) ) {
		return jstr;
	}
	TDbCol def = view.ColDef(aColIndex);
	jint colType = def.iType;

	if ( colType == EDbColText8) {
		TPtrC8 tmp = view.ColDes8(aColIndex);
		RBuf buf;
		TInt res = buf.Create(tmp.Length());
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			return jstr;
		}
		buf.Copy(tmp);
		jstr = CreateJavaString(aEnv, buf);
	} else if ( colType == EDbColLongText8 ) {
		TInt blobLength = view.ColLength(aColIndex);
		RBuf8 cbuf;
		TInt res = cbuf.Create(blobLength);
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			return jstr;
		}

		RDbColReadStream blob;
		TRAP(res, blob.OpenL(view,aColIndex));
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			cbuf.Close();
			return jstr;
		}
		TRAP(res, blob.ReadL(cbuf, blobLength));
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			cbuf.Close();
			blob.Release();
			blob.Close();
			return jstr;
		}
		blob.Release();
		blob.Close();

		RBuf buf;
		res = buf.Create(cbuf.Length());
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			cbuf.Close();
			return jstr;
		}
		buf.Copy(cbuf);
		cbuf.Close();
		jstr = CreateJavaString(aEnv, buf);
		buf.Close();
	} else if ( colType == EDbColLongText16 ) {
		TInt blobLength = view.ColLength(aColIndex);
		RBuf cbuf;
		TInt res = cbuf.Create(blobLength);
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			return jstr;
		}

		RDbColReadStream blob;
		TRAP(res, blob.OpenL(view,aColIndex));
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			cbuf.Close();
			return jstr;
		}
		TRAP(res, blob.ReadL(cbuf, blobLength));
		if ( res != KErrNone ) {
			ThrowExc(aEnv, res );
			cbuf.Close();
			blob.Release();
			blob.Close();
			return jstr;
		}
		blob.Release();
		blob.Close();

		jstr = CreateJavaString(aEnv, cbuf);
		cbuf.Close();
	} else {
		// 16 bit / wide string
		TPtrC ptr = view.ColDes16(aColIndex);
		jstr = CreateJavaString(aEnv, ptr);
	}

	return jstr;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getBytes
 * Signature: (I)[B
 */
JNIEXPORT jbyteArray JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getBytes
  (JNIEnv *aEnv, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	jbyteArray array = NULL;
	TDbColNo colNo(aColIndex);
	if ( view.IsColNull(colNo) ) {
		return array;
	}
	TDbCol col = view.ColDef(aColIndex);
	TInt colType = col.iType;
	TInt size = view.ColSize(aColIndex);
	if ( colType == EDbColBinary ) {
		TPtrC8 buf = view.ColDes8(aColIndex);
		array = aEnv->NewByteArray(size);
		aEnv->SetByteArrayRegion(array, 0, size, (jbyte*)buf.Ptr());
		return array;
	} else {
		RDbColReadStream stream;
		TRAPD(err, stream.OpenL(view, aColIndex));
		if ( err != KErrNone ) {
			ThrowExc(aEnv, err );
			return array;
		}

		// read from stream into buffer
		RBuf8 buf;
		err = buf.Create(size);
		if ( err != KErrNone ) {
			ThrowExc(aEnv, err );
			stream.Release();
			stream.Close();
			return array;
		}

		stream.ReadL(buf, size);
		stream.Release();
		stream.Close();
		array = aEnv->NewByteArray(size);
		aEnv->SetByteArrayRegion(array, 0, size, (jbyte*)buf.Ptr());
		buf.Close();
		return array;
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsResultSet
 * Method:    _getDouble
 * Signature: (I)D
 */
JNIEXPORT jdouble JNICALL Java_com_symbian_dbms_jdbc_DbmsResultSet__1getDouble
  (JNIEnv *, jobject, jint aPeerHandle, jint aColIndex){
	DbmsResultSet* rset = (DbmsResultSet*) aPeerHandle;
	RDbView& view = rset->iStatement->iView;
	return (jdouble) view.ColReal64(aColIndex);
}
