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

#include <e32std.h>
#include <e32des8.h>
#include <jni.h>

//----------------------------------------------------------------------------
// RJString takes a Java JNI string and converts it to an
// Epoc string. It retains the JNI environment and the string
// in order to release the string resources during destruction
class RJString : public TPtrC16
	{
public:
	RJString( JNIEnv& aJni, jstring aString );
	~RJString();

private:
	// Prevent accidental copying because of the shared underlying Java
	// string
	RJString( const RJString& );
	RJString& operator=( const RJString& );

private:
	JNIEnv& iJni;
	jstring iString;
	};

//----------------------------------------------------------------------------
jstring CreateJavaString( JNIEnv* aJni, const TDesC16& aString );

void SosPanicHandler(const TDesC& aCat, TInt aReason);

void ThrowRtExc(JNIEnv* aJni, const TDesC8& aMessage );

void ThrowExc(JNIEnv* aJni, const TDesC8& aException, const TDesC8& aMessage );

void ThrowExc(JNIEnv* aJni, const TInt aErrorCode );

void GetException(TInt aErrorCode, TDes8& aBuf, TDes8& aMessage);
