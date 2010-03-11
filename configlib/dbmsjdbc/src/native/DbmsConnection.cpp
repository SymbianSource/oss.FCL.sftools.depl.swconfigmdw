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
#include "DbmsConnection.h"
#include "Utils.h"
#include "dbmsjni/com_symbian_dbms_jdbc_DbmsConnection.h"
#include <stdlib.h>
#include <stdio.h>

CTrapCleanup* gCleanup = NULL; // get clean-up stack
TInt gConnectionCount = 0;
jclass gExcCls = NULL;
TUint32 gThirdUid = 0;

extern TPanicHandler gPanicHandler;
extern TInt gBlockSize;
extern TInt gClusterSize;
extern TExtendedLocale gLocale;

// //
// DbmsConnection peer
// //

DbmsConnection::DbmsConnection(){
	iOpen = EFalse;
}

DbmsConnection::~DbmsConnection(){
}

TInt DbmsConnection::Open(const TDesC& aFileName){
	RFs fs;
	TInt res = iDatabase.Open(fs, aFileName);
	if ( res == KErrNotFound ) {
		if ( gThirdUid != 0 ) {
			TBuf<64> buf;
			buf.Append(_L("SECURE["));
			buf.AppendNum(gThirdUid, EHex);
			buf.Append(_L("]"));
			res = iDatabase.Create(fs, aFileName, buf);
		} else {
			res = iDatabase.Create(fs, aFileName);
		}
	}
	if ( res == KErrNone ) {
		iOpen = ETrue;
	}
	return res;
}

void DbmsConnection::Close(){
	if ( iOpen )
		{
		iDatabase.Compact();
		}
	iDatabase.Close();
	iOpen = EFalse;
}

// //
// JNI
// //

/*
 * Class:     com_symbian_dbms_jdbc_DbmsConnection
 * Method:    _globalInit
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1globalInit
  (JNIEnv *aEnv, jobject) {
	if ( gCleanup == NULL ) {
		// init globals
		gCleanup=CTrapCleanup::New(); // get clean-up stack
		gPanicHandler = &SosPanicHandler;
		jclass excCls = aEnv->FindClass("java/lang/RuntimeException");
		if ( excCls == NULL )
			{
			printf("Could not create exception class java/lang/RuntimeException in DbmsConnection::init ...\n");
			}
		else
			{
			gExcCls = (jclass)(aEnv->NewGlobalRef(excCls));
			if ( gExcCls == NULL )
				{
				printf("Could not create glref to exception class java/lang/RuntimeException in DbmsConnection::init ...\n");
				}
			}
	}
}


JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1init
  (JNIEnv *aEnv, jobject aObject, jstring aString) {
	gConnectionCount++;
	DbmsConnection* connection = new DbmsConnection();
	RJString file(*aEnv, aString);
	TInt res = connection->Open(file);
	if ( res != KErrNone ){
		connection->Close();
		delete connection;
		return (jint) res;
	} else {
		return (jint) connection;
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsConnection
 * Method:    _setSecureId
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1setSecureId
  (JNIEnv *, jobject, jint aSecureId) {
	gThirdUid = aSecureId;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsConnection
 * Method:    _close
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1close
  (JNIEnv * aEnv, jobject aJavaObj, jint aPeer) {
	DbmsConnection* connection = (DbmsConnection*) aPeer;
	connection->Close();
	delete connection;
	gConnectionCount--;
	if ( gConnectionCount == 0 && gCleanup != NULL ) {
		delete gCleanup;
		gCleanup = NULL;
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsConnection
 * Method:    _setLocaleDll
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1setLocaleDll
  (JNIEnv *aEnv, jobject, jstring aDllFile){
	RJString rj(*aEnv, aDllFile);
	return gLocale.LoadLocale(rj);
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsConnection
 * Method:    _setBlockSize
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1setBlockSize
  (JNIEnv *, jobject, jint aBlockSize){
	gBlockSize = aBlockSize;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsConnection
 * Method:    _setClusterSize
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1setClusterSize
  (JNIEnv *, jobject, jint aClusterSize){
	gClusterSize = aClusterSize;
}


void PrintColTypeName(TDes8& aDes, TDbCol& col)
	{
	_LIT8(KNotNull, "not-null ");
	_LIT8(KAutoIncrement, "auto-increment");
	_LIT8(KColNameInt8, "EDbColInt8");
	_LIT8(KColNameInt16, "EDbColInt16");
	_LIT8(KColNameInt32, "EDbColInt32");
	_LIT8(KColNameInt64, "EDbColInt64");
	_LIT8(KColNameUInt8, "EDbColUint8");
	_LIT8(KColNameUInt16, "EDbColUint16");
	_LIT8(KColNameUInt32, "EDbColUint32");
	_LIT8(KColNameBit, "EDbColBit");
	_LIT8(KColNameReal32,"EDbColReal32");
	_LIT8(KColNameReal64,"EDbColReal64");
	_LIT8(KColNameDateTime,"EDbColDateTime");
	_LIT8(KColNameBinary,"EDbColBinary");
	_LIT8(KColNameText8,"EDbColText8");
	_LIT8(KColNameText16,"EDbColText16");
	_LIT8(KColNameLongBinary,"EDbColLongBinary");
	_LIT8(KColNameLongText8,"EDbColLongText8");
	_LIT8(KColNameLongText16,"EDbColLongText16");
	_LIT8(KFormattingPrefix, "| ");
	aDes.Append(KFormattingPrefix);
	switch ( col.iType )
		{
		case EDbColInt8:
			{
			aDes.Append(KColNameInt8);
			break;
			}
		case EDbColInt16:
			{
			aDes.Append(KColNameInt16);
			break;
			}
		case EDbColInt32:
			{
			aDes.Append(KColNameInt32);
			break;
			}
		case EDbColInt64:
			{
			aDes.Append(KColNameInt64);
			break;
			}
		case EDbColUint8:
			{
			aDes.Append(KColNameUInt8);
			break;
			}
		case EDbColUint16:
			{
			aDes.Append(KColNameUInt16);
			break;
			}
		case EDbColUint32:
			{
			aDes.Append(KColNameUInt32);
			break;
			}
		case EDbColBit:
			{
			aDes.Append(KColNameBit);
			break;
			}
		case EDbColReal32:
			{
			aDes.Append(KColNameReal32);
			break;
			}
		case EDbColReal64:
			{
			aDes.Append(KColNameReal64);
			break;
			}
		case EDbColDateTime:
			{
			aDes.Append(KColNameDateTime);
			break;
			}
		case EDbColBinary:
			{
			aDes.Append(KColNameBinary);
			break;
			}
		case EDbColText8:
			{
			aDes.Append(KColNameText8);
			aDes.Append('[');
			aDes.AppendNum(col.iMaxLength);
			aDes.Append(']');
			break;
			}
		case EDbColText16:
			{
			aDes.Append(KColNameText16);
			aDes.Append('[');
			aDes.AppendNum(col.iMaxLength);
			aDes.Append(']');
			break;
			}
		case EDbColLongBinary:
			{
			aDes.Append(KColNameLongBinary);
			break;
			}
		case EDbColLongText8:
			{
			aDes.Append(KColNameLongText8);
			break;
			}
		case EDbColLongText16:
			{
			aDes.Append(KColNameLongText16);
			break;
			}
		} // end switch
		TInt len = aDes.Length();
		for (TInt i = len; i < 46 ; i++ )
			aDes.Append(' ');

		aDes.Append(KFormattingPrefix);
		if ( col.iAttributes & TDbCol::ENotNull )
			{
			aDes.Append(KNotNull);
			}
		if ( col.iAttributes & TDbCol::EAutoIncrement )
			{
			aDes.Append(KAutoIncrement);
			}
	}


jstring DumpSchemaL(JNIEnv *aEnv, jobject, jint aPeer){
	_LIT8(KSchemaTableLabel, "Table: ");
	_LIT8(KSchemaIndexLabel, "| INDEX: ");
	_LIT8(KLine, "----------------------------------------------------------------------------\n");
	DbmsConnection* connection = (DbmsConnection*) aPeer;
	RDbNamedDatabase& db = connection->iDatabase;
	TInt KMaxSchemaSize = 1024*1024; // 1Mb

	CDbTableNames* tableNames = db.TableNamesL();
	RBuf8 resultBuf;
	RBuf retBuf;
	TBuf8<512> printBuf;
	TInt err = resultBuf.Create(KMaxSchemaSize);
	if ( err != KErrNone ) {
		ThrowExc(aEnv, err );
		return NULL;
	}
	err = retBuf.Create(KMaxSchemaSize);
	if ( err != KErrNone ) {
		resultBuf.Close();
		ThrowExc(aEnv, err );
		return NULL;
	}
	for (int i = 0; i < tableNames->Count(); i++ )
		{
		TBuf<64> tableName;
		tableName.Copy((*tableNames)[i]);
		printBuf.Copy(KSchemaTableLabel);
		printBuf.Append(tableName);
		resultBuf.Append(	KLine);
		resultBuf.Append(_L8("| "));
		resultBuf.Append(printBuf);
		for( TInt j = printBuf.Length() ; j < 74; j++)
			resultBuf.Append(_L8(" "));
		resultBuf.Append(_L8("|\n"));
		resultBuf.Append(KLine);

		CDbColSet* colSet = db.ColSetL(tableName);
		CleanupStack::PushL(colSet);
		printBuf.Zero();

		resultBuf.Append(_L8("| Column name               "));
		resultBuf.Append(_L8("| Type              "));
		resultBuf.Append(_L8("| Flags                    |\n"));
		resultBuf.Append(KLine);
		for ( TInt ii = 0 ; ii < colSet->Count() ; ii++ )
			{
			TDbCol col = (*colSet)[ii+1];
			TBuf8<128> cn;
			cn.Copy(col.iName);
			printBuf.Copy(cn);
			printBuf.Append(' ');
			for(TInt j = cn.Length() ; j < 25; j++ )
				printBuf.Append(' ');
			PrintColTypeName(printBuf, col);
			printBuf.Append(' ');
			resultBuf.Append(_L8("| "));
			resultBuf.Append(printBuf);
			for( TInt j = printBuf.Length() ; j < 74; j++)
				resultBuf.Append(_L8(" "));
			resultBuf.Append(_L8("|\n"));
			}

		CleanupStack::PopAndDestroy();

		// indices
		_LIT8(KPrimary, " PRIMARY KEY ");
		_LIT8(KUnique, " UNIQUE ");
		_LIT8(KFolded, " Comparison: FOLDED ");
		_LIT8(KCollated, " Comparison: COLLATED ");
		_LIT8(KNormal, " Comparison: NORMAL ");

		CDbIndexNames* indexNames = db.IndexNamesL(tableName);

		if ( indexNames->Count() > 0 )
			resultBuf.Append(KLine);

		for (int j = 0; j < indexNames->Count(); j++ )
			{
			TBuf<64> indexName;
			indexName.Copy((*indexNames)[j]);
			printBuf.Copy(KSchemaIndexLabel);
			printBuf.Append(indexName);
			printBuf.Append(' ');
			printBuf.Append('(');
			printBuf.Append(' ');
			CDbKey* key = db.KeyL(indexName, tableName);
			CleanupStack::PushL(key);
			// indexed columns
			for ( int k = 0 ; k < key->Count(); k ++ )
				{
				if ( k != 0 )
					{
					printBuf.Append(',');
					printBuf.Append(' ');
					}
				TDbKeyCol col = (*key)[k];
				printBuf.Append(col.iName);
				}
			printBuf.Append(' ');
			printBuf.Append(')');
			printBuf.Append(' ');
			if ( key->IsPrimary() )
				{
				printBuf.Append(KPrimary);
				}
			if ( key->IsUnique() )
				{
				printBuf.Append(KUnique);
				}
			switch ( key->Comparison() )
				{
				case EDbCompareNormal:
					{
					printBuf.Append(KNormal);
					break;
					}
				case EDbCompareFolded:
					{
					printBuf.Append(KFolded);
					break;
					}
				case EDbCompareCollated:
					{
					printBuf.Append(KCollated);
					break;
					}
				}
			CleanupStack::PopAndDestroy();

			resultBuf.Append(printBuf);
			for( TInt j = printBuf.Length() ; j < 76; j++)
				resultBuf.Append(_L8(" "));
			resultBuf.Append(_L8("|\n"));
			}

		resultBuf.Append(KLine);
		resultBuf.Append(_L8("\n"));
		}
	delete tableNames;
	// create java string - must copy into 16 bit desc
	retBuf.Copy(resultBuf);
	resultBuf.Close();
	jstring jret = CreateJavaString( aEnv, retBuf );
	retBuf.Close();
	return jret;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsConnection
 * Method:    _schema
 * Signature: (I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_symbian_dbms_jdbc_DbmsConnection__1schema
  (JNIEnv *aEnv, jobject aObj, jint aPeer) {
	jstring ret = NULL;
	TRAPD(err, ret = DumpSchemaL(aEnv, aObj, aPeer));
	if ( err != KErrNone ) {
		ThrowExc(aEnv, err );
		return NULL;
	}
	return ret;
}
