// Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
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

/*
 ============================================================================
 Name		: SdbTestFramework.h
 Author	  : 
 Copyright   : Your copyright notice
 Description : SdbTestFramework.h - CSdbTestFramework class header
 ============================================================================
 */

// This file defines the API for SdbTestFramework.dll

#ifndef __SDBTESTFRAMEWORK_H__
#define __SDBTESTFRAMEWORK_H__

//  Include Files

#include <e32base.h>
#include <e32std.h>	
#include <e32test.h>
#include <f32file.h>
#include <bacline.h>

//  Constants

//  Class Definitions
class RSdbTest
	{
public:
	/**
	 * Default constructor.
	 */
	IMPORT_C RSdbTest();
	/**
	 * Create a test with a title.
	 */
	IMPORT_C RSdbTest(const TDesC& aTitle);
	/**
	 * Prints the test title to console.
	 */
	IMPORT_C void Title();
	/**
	 * Does cleanup - effectively acts as destructor. After calling CloseL, a test 
	 * cannot be used.
	 * <p>
	 * Closing a test has several consequences:
	 * <p>
	 * 1. CloseL calls EndL with KErrNone <br> 
	 * 2. Console is destroyed. 
	 * 3. Command line is destroyed. 
	 * 4. File server session is closed.
	 * 
	 * Trying to use most test functions after a call to CloseL results in Panic. <br>     
	 */
	IMPORT_C void CloseL();
	
	/**
	 * Start test execution. This must be called before calls to any test methods.
	 */
	IMPORT_C void StartL(const TDesC &aHeading);
	
	/**
	 * Exactly same behaviour as RTest::Next.
	 */
	IMPORT_C void Next(const TDesC &aHeading);

	/**
	 * End the test. This function writes out the given result to 
	 * the test result file which will be read by Java wrapper.
	 */
	IMPORT_C void EndL(TInt aExitValue);

	/**
	 * Write arbitrary text to console.
	 */
	IMPORT_C void Printf(TRefByValue<const TDesC> aFmt,...);
	
	/**
	 * Read a charater from console. Only available in DEBUG mode
	 * to allow for un-interrupted automated testing.
	 * 
	 * @see SetDebugMode
	 */
	IMPORT_C TKeyCode Getch();
	
	/**
	 * Get the command line arguments. Note that ownership
	 * of the object remains with RSdbTest so API users do not need to
	 * manage the object.
	 */
	IMPORT_C CCommandLineArguments* CommandLineArgumentsL();

	/**
	 * Set the output file name where EndL should write result.
	 * The result is read by Java wrapper.
	 */
	IMPORT_C void SetOutputFileName(const TDesC& aFileName);

	/**
	 * Get the output file name where EndL should write result.
	 * The result is read by Java wrapper.
	 */
	IMPORT_C TDesC& GetOutputFileName();
	
	/**
	 * Get the console.
	 */
	IMPORT_C CConsoleBase* Console() const;
	
	/**
	 * Set the console.
	 */
	IMPORT_C void SetConsole(CConsoleBase* aConsole);
	
	/**
	 * Test weather logging to file is enabled.
	 */
	IMPORT_C TBool Logged() const;
	
	/**
	 * Enable or disable logging to file.
	 */
	IMPORT_C void SetLogged(TBool aToLog);
	
	
	/**
	 * Check if aValue is true, leave if not.
	 * On failure, this function calls EndL with the leave code KErrGeneral
	 * therefore informing the Java wrapper of the test failure. 
	 */
	IMPORT_C void AssertTrueL(TBool aValue);
	
	/**
	 * Check if aValue is KErrNone, leave if not.
	 * On failure, this function calls EndL with aValue as the leave code 
	 * therefore informing the Java wrapper of the test failure. 
	 */
	IMPORT_C void AssertNotErrorL(TInt aValue);
	
	/**
	 * Check if aValue is true, leave if not.
	 * On failure, this function calls EndL with the leave code KErrGeneral
	 * therefore informing the Java wrapper of the test failure. 
	 * @aLine Line number - use __LINE__ macro to automatically add line numbers
	 */
	IMPORT_C void AssertTrueL(TBool aValue, TInt aLine);

	/**
	 * Check if aValue is KErrNone, leave if not.
	 * On failure, this function calls EndL with aValue as the leave code 
	 * therefore informing the Java wrapper of the test failure. 
	 * @aLine Line number - use __LINE__ macro to automatically add line numbers
	 */
	IMPORT_C void AssertNotErrorL(TInt aValue, TInt aLine);

	/**
	 * Check if aValue is true, leave if not.
	 * On failure, this function calls EndL with the leave code KErrGeneral
	 * therefore informing the Java wrapper of the test failure. 
	 * @aComment Textual comment to print if test fails.
	 * @aLine Line number - use __LINE__ macro to automatically add line numbers
	 */
	IMPORT_C void AssertTrueL(TBool aValue, const TDesC& aComment, TInt aLine);

	/**
	 * Check if aValue is KErrNone, leave if not.
	 * On failure, this function calls EndL with aValue as the leave code 
	 * therefore informing the Java wrapper of the test failure. 
	 * @aComment Textual comment to print if test fails.
	 * @aLine Line number - use __LINE__ macro to automatically add line numbers
	 */
	IMPORT_C void AssertNotErrorL(TInt aValue, const TDesC& aComment, TInt aLine);

	/**
	 * Check if aValue is true, leave if not.
	 * On failure, this function calls EndL with the leave code KErrGeneral
	 * therefore informing the Java wrapper of the test failure. 
	 * @aComment Textual comment to print if test fails.
	 */
	IMPORT_C void AssertTrueL(TBool aValue, const TDesC& aComment);

	/**
	 * Check if aValue is KErrNone, leave if not.
	 * On failure, this function calls EndL with aValue as the leave code 
	 * therefore informing the Java wrapper of the test failure. 
	 * @aComment Textual comment to print if test fails.
	 */
	IMPORT_C void AssertNotErrorL(TInt aValue, const TDesC& aComment);
	
	/**
	 * If set to ETrue, calls to Getch will block.
	 * If set to EFalse, calls to Getch will immediately return EKeyNull.
	 */
	IMPORT_C void SetDebugMode(TBool aDebug);
	 
private:
	RTest iTest;
	RFs   iFs;
	TBuf<256> iOutputFileName;
	CCommandLineArguments* iCommandLineArguments;
	TBool iEnded;
	TBool iClosed;
	TBool iDebug;
	};

#endif  // __SDBTESTFRAMEWORK_H__

