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

package com.symbian.sdb.contacts.dbms.model;

import com.symbian.sdb.contacts.model.IHint;
import com.symbian.sdb.contacts.model.TemplateHint;

/**
 * @author krzysztofZielinski
 *
 */
public class TemplateHintField {

	private int value;
	
    // ~ Constructors ==========================================================
    
    /**
     * @param value
     */
    public TemplateHintField(String fieldType) {
		if (fieldType.equals("KUidContactFieldAddressValue")) {
			setField(TemplateHint.KIntContactHintIsAddress);
		}
		else if (fieldType.equals("KUidContactFieldCompanyNameValue")) {
			setField(TemplateHint.KIntContactHintIsCompanyName);
		}
		else if (fieldType.equals("KUidContactFieldPhoneNumberValue")) {
			setField(TemplateHint.KIntContactHintIsPhone);
		}
		else if (fieldType.equals("KUidContactFieldGivenNameValue")) {
			setField(TemplateHint.KIntContactHintIsGivenName);
		}
		else if (fieldType.equals("KUidContactFieldFamilyNameValue")) {
			setField(TemplateHint.KIntContactHintIsFamilyName);
		}
		else if (fieldType.equals("KUidContactFieldCompanyNamePronunciationValue")) {
			setField(TemplateHint.KIntContactHintIsCompanyNamePronunciation);
		}
		else if (fieldType.equals("KUidContactFieldGivenNamePronunciationValue")) {
			setField(TemplateHint.KIntContactHintIsGivenNamePronunciation);
		}
		else if (fieldType.equals("KUidContactFieldFamilyNamePronunciationValue")) {
			setField(TemplateHint.KIntContactHintIsFamilyNamePronunciation);
		}
		else if (fieldType.equals("KUidContactFieldAdditionalNameValue")) {
			setField(TemplateHint.KIntContactHintIsAdditionalName);
		}
		else if (fieldType.equals("KUidContactFieldSuffixNameValue")) {
			setField(TemplateHint.KIntContactHintIsSuffixName);
		}
		else if (fieldType.equals("KUidContactFieldPrefixNameValue")) {
			setField(TemplateHint.KIntContactHintIsPrefixName);
		}
		else if (fieldType.equals("KUidContactFieldEMailValue")) {
			setField(TemplateHint.KIntContactHintIsEmail);
		}
		else if (fieldType.equals("KUidContactFieldMsgValue")) {
			setField(TemplateHint.KIntContactHintIsMsg);
		}
		else if (fieldType.equals("KUidContactFieldStorageInlineValue")) {
			setField(TemplateHint.KIntContactHintStorageInline);
		}	
    }

    // ~ Business Methods ======================================================
    
    public void setField(IHint templateHint)  {
        this.value |= templateHint.getValue();
    }
    
    public int getValue() {
        return value;
    }
}
