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
#include "DbmsStatement.h"
#include "DbmsConnection.h"
#include "DbmsResultSet.h"
#include "Utils.h"
#include "dbmsjni/com_symbian_dbms_jdbc_DbmsStatement.h"
#include <stdlib.h>

// //
// DbmsStatement peer
// //

DbmsStatement::DbmsStatement(DbmsConnection* aConnection){
	iConnection = aConnection;
}

DbmsStatement::~DbmsStatement(){
}

void DbmsStatement::Close(){
	iView.Close();
}

// //
// JNI
// //

/*
 * Class:     com_symbian_dbms_jdbc_DbmsStatement
 * Method:    _create
 * Signature: (I)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsStatement__1create
  (JNIEnv *, jobject, jint aPeer){
	DbmsConnection* connection = (DbmsConnection*) aPeer;
	DbmsStatement* statement = new DbmsStatement(connection);
	return (jint) statement;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsStatement
 * Method:    _executeUpdate
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsStatement__1executeUpdate
  (JNIEnv *aEnv, jobject, jint aPeer, jstring aString){
	DbmsStatement* statement = (DbmsStatement*) aPeer;
	RJString sql(*aEnv, aString);
	RDbNamedDatabase& db = statement->iConnection->iDatabase;
	TInt res = db.Execute(sql);
	return res;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsStatement
 * Method:    _executeQuery
 * Signature: (ILjava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsStatement__1executeQuery
  (JNIEnv *aEnv, jobject, jint aPeer, jstring aString){
	DbmsStatement* statement = (DbmsStatement*) aPeer;
	RJString sql(*aEnv, aString);
	TDbQuery query (sql);
	TInt res = statement->iView.Prepare(statement->iConnection->iDatabase, query, RDbRowSet::EReadOnly);
	if ( res < 0 ) {
		return (jint) res;
	} else {
		res = statement->iView.EvaluateAll();
		if ( res < 0 ) {
			return (jint) res;
		} else {
			DbmsResultSet* resultSet = new DbmsResultSet(statement);
			return (jint) resultSet;
		}
	}
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsStatement
 * Method:    _close
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsStatement__1close
  (JNIEnv *, jobject, jint aPeer){
	DbmsStatement* statement = (DbmsStatement*) aPeer;
	statement->Close();
	delete statement;
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsStatement
 * Method:    _begin
 * Signature: (I)V
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsStatement__1begin
  (JNIEnv *, jobject, jint aPeer) {
	DbmsStatement* statement = (DbmsStatement*) aPeer;
	return statement->iConnection->iDatabase.Begin();
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsStatement
 * Method:    _commit
 * Signature: (I)V
 */
JNIEXPORT jint JNICALL Java_com_symbian_dbms_jdbc_DbmsStatement__1commit
  (JNIEnv *, jobject, jint aPeer) {
	DbmsStatement* statement = (DbmsStatement*) aPeer;
	return statement->iConnection->iDatabase.Commit();
}

/*
 * Class:     com_symbian_dbms_jdbc_DbmsStatement
 * Method:    _rollback
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_com_symbian_dbms_jdbc_DbmsStatement__1rollback
  (JNIEnv *, jobject, jint aPeer) {
	DbmsStatement* statement = (DbmsStatement*) aPeer;
	statement->iConnection->iDatabase.Rollback();
}


