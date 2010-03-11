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

package com.symbian.sdb.cmd;

import java.util.List;
import java.util.ListIterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.cli2.validation.InvalidArgumentException;
import org.apache.commons.cli2.validation.Validator;
import com.symbian.sdb.mode.IModeParser;
import com.symbian.sdb.mode.ModeParser;
import com.symbian.sdb.settings.Settings;

/**
 * Custom validator class for mode value
 */
public class ModeValidator implements Validator {

	/**
	 * validates the mode option value during the command line parsing
	 * if the value is incorrect the InvalidArgumentException is thrown
	 * correct current values for mode are:
	 * - sqlite
	 * - dbms
	 * - sqlite.contacts
	 * - dbms.contacts
	 * - ced
	 * - ced.[schema] where schema can be a sequence of numbers separated by dots
	 * 
	 * Exchanges original {@link String} mode parameter with {@link ModeParser} object
	 */
	@SuppressWarnings("unchecked")
	public void validate(List values) throws InvalidArgumentException {
		if (values.size() != 1) {
			throw new InvalidArgumentException("Invalid number of mode option arguments.");
		}
		String validation = getModeValidationRegExp();
		
		Pattern pattern = Pattern.compile(validation);
		for (final ListIterator i = values.listIterator(); i.hasNext();) {
			if (i.next() instanceof String) {
	    		String mode = (String) i.previous();
	    		i.next(); // need to move 1 place forward
	    		
	            Matcher matcher = pattern.matcher(mode);

	            if (!matcher.matches()) {
	                throw new InvalidArgumentException(mode);
	            }
	            
	            IModeParser parser = new ModeParser(mode);
	            i.set(parser);
			}
			else {
				throw new InvalidArgumentException("Invalid mode option argument");
			}   
		}
	}

	/**
	 * @return
	 */
	private String getModeValidationRegExp() {
		String contactsModeRegExp;
		if(Settings.isContactsEnabled()){
			contactsModeRegExp = "(\\.contacts)?";
		}
		else {
			contactsModeRegExp = "";
		}
		String validationRegExp = "((sqlite|dbms)" + contactsModeRegExp + "|ced(\\.9[1-5]))";
		return validationRegExp;
	}
}
