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

#include "Utils.h"
#include <utf.h>
#include <stdio.h>
#include <stdlib.h>
#include <errortranslator.h>


JavaVM* gJVM;
extern jclass gExcCls;

jint JNI_OnLoad(JavaVM *vm, void *reserved)
	{
	gJVM = vm;
    return JNI_VERSION_1_4;
	}

extern TPanicHandler gPanicHandler;

/**
 * Constuctor taking a Java JNI string and converting it to an EPOC TPtrC.
 */
RJString::RJString( JNIEnv& aJni, jstring aString )
: iJni( aJni ), iString( aString )
	{
	// Potential for a string to be NULL, but NULL cannot be passed into
	// JNI methods, so must check. If string is NULL, will result in empty string
	if ( iString != NULL )
		{
		Set( aJni.GetStringChars( iString, NULL ), aJni.GetStringLength( iString ) );
		}
	}



/**
 * Frees up the JNI string resources, if they need to be freed.
 */
RJString::~RJString()
	{
	if ( iString != NULL )
		{
		iJni.ReleaseStringChars( iString, this->Ptr() );
		}
	}

//----------------------------------------------------------------------------
/* Takes an EPOC string and returns a Java JNI string */
jstring CreateJavaString( JNIEnv* aJni, const TDesC& aString )
	{
	const jchar* stringPtr = aString.Ptr();
	const jsize stringLength = aString.Length();
	jstring jniString = aJni->NewString( stringPtr, stringLength );
	return jniString;
	}

void ThrowRtExc(JNIEnv* aJni, const TDesC8& aMessage )
	{
	if ( gExcCls ==NULL )
		{
		printf("Could not create exception class java/lang/RuntimeException, unable to throw\n");
		return;
		}
	aJni->ThrowNew(gExcCls, (const char*) aMessage.Ptr());
	}

void ThrowExc(JNIEnv* aJni, const TDesC8& aException, const TDesC8& aMessage )
	{
	jclass jc = aJni->FindClass((const char *)aException.Ptr());
	if ( jc == NULL ) {
		jc = gExcCls;
	}
	aJni->ThrowNew(jc, (const char*) aMessage.Ptr());
	}

void ThrowExc(JNIEnv* aJni, const TInt aErrorCode )
	{
	TBuf8<256> exception;
	TBuf8<256> message;
	GetException(aErrorCode, exception, message);
	exception.ZeroTerminate();
	message.ZeroTerminate();
	jclass jc = aJni->FindClass((const char *)exception.Ptr());
	if ( jc == NULL ) {
		jc = gExcCls;
	}
	aJni->ThrowNew(jc, (const char*) message.Ptr());
	}


void SosPanicHandler(const TDesC& aCat, TInt aReason)
	{
	_LIT8(KPanicString, " [SOS Panic]");
	_LIT8(KSpace, " : ");
	TBuf8<512> exceptionMessage;
	exceptionMessage.Copy(aCat);
	exceptionMessage.Append(KSpace);
	exceptionMessage.AppendNum(aReason);
	exceptionMessage.Append(KPanicString);
	exceptionMessage.Append('\0');
	// Get the JNIEnv
	JNIEnv* env;
	int res = gJVM->GetEnv((void**)&env, JNI_VERSION_1_4);

	if ( res == JNI_EDETACHED )
		{
		printf("Attaching to the current thread...\n");
		res = gJVM->AttachCurrentThread((void**)&env, NULL);
		}

	if ( res < 0 )
		{
		printf("Could not attach current thread while handling panic!");
		exit(-1);
		}
	ThrowRtExc(env, exceptionMessage);
	//printf("SOS panic handled by JNI : %s\n", (const char*)exceptionMessage.Ptr());
	}



const TInt KMaxExceptionClassNameLength = 200;
static const TText8 KExceptionClassNames[][KMaxExceptionClassNameLength+1]=
	{
#define EXCEPTIONNAME(s) #s
#include "exceptionmappings.h"
#undef EXCEPTIONNAME
	};


void GetException(TInt aErrorCode, TDes8& aException, TDes8& aMessage)
	{
	_LIT8(KRuntimeException, "java/lang/RuntimeException");
	TranslateError(aErrorCode, aMessage);
	aErrorCode = - aErrorCode;
	if ( aErrorCode > 46 || aErrorCode < 0)
		{
		aException.Copy(KRuntimeException);
		}
	else
		{
		aException.Copy(KExceptionClassNames[aErrorCode]);
		}
	}

