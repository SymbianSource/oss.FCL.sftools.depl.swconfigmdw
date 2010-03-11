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

package com.symbian.sdb.contacts.model;

public enum TemplateHint implements IHint {
	
	KIntContactHintIsPhone((short) 0x02, "KUidContactFieldPhoneNumberValue"),
	KIntContactHintIsMsg((short) 0x04, "KUidContactFieldMsgValue"),
	KIntContactHintIsCompanyName((short) 0x08, "KUidContactFieldCompanyNameValue"),
	KIntContactHintIsFamilyName((short) 0x10, "KUidContactFieldFamilyNameValue"),
	KIntContactHintIsGivenName((short) 0x20, "KUidContactFieldGivenNameValue"),
	KIntContactHintIsAddress((short) 0x40, "KUidContactFieldAddressValue"),
	KIntContactHintIsAdditionalName((short) 0x80, "KUidContactFieldAdditionalNameValue"),
	KIntContactHintIsSuffixName((short) 0x100, "KUidContactFieldSuffixNameValue"),
	KIntContactHintIsPrefixName((short) 0x200, "KUidContactFieldPrefixNameValue"),
	KIntContactHintIsPronunciation((short) 0x800, ""),
	
	KIntContactHintIsEmail((short) 0x4000, "KUidContactFieldEMailValue"),
	KIntContactHintStorageInline((short) 0x400, "KUidContactFieldStorageInlineValue"),
	KIntContactHintIsCompanyNamePronunciation((short) (KIntContactHintIsPronunciation.getValue() | KIntContactHintIsCompanyName.getValue()), "KUidContactFieldCompanyNamePronunciationValue"),
	KIntContactHintIsGivenNamePronunciation((short) (KIntContactHintIsPronunciation.getValue() | KIntContactHintIsGivenName.getValue()), "KUidContactFieldGivenNamePronunciationValue"),
	KIntContactHintIsFamilyNamePronunciation((short) (KIntContactHintIsPronunciation.getValue() | KIntContactHintIsFamilyName.getValue()), "KUidContactFieldFamilyNamePronunciationValue");

    private short _value;
    private String _uid;    
    
	private TemplateHint(short value, String uid) {
		_value = value;
		_uid = uid;
	}
    
	public short getValue(){
		return _value;
	}
	
	public String getUid() {
		return _uid;
	}
	
	public static TemplateHint[] dbmsTemplateValues() {
		return new TemplateHint[]{
				KIntContactHintIsPhone, 
				KIntContactHintIsMsg,	
				KIntContactHintIsCompanyName, 
				KIntContactHintIsFamilyName, 
				KIntContactHintIsGivenName, 
				KIntContactHintIsAddress,
				KIntContactHintIsAdditionalName, 
				KIntContactHintIsSuffixName,
				KIntContactHintIsPrefixName,
				KIntContactHintIsPronunciation, 
				KIntContactHintIsEmail, 
				KIntContactHintStorageInline,
				KIntContactHintIsCompanyNamePronunciation, 
				KIntContactHintIsGivenNamePronunciation,
				KIntContactHintIsFamilyNamePronunciation
				};
	}
	
	public static TemplateHint[] sqliteTemplateValues() {
		return new TemplateHint[]{KIntContactHintIsPhone, 
				KIntContactHintIsMsg,	
				KIntContactHintIsCompanyName, 
				KIntContactHintIsFamilyName, 
				KIntContactHintIsGivenName, 
				KIntContactHintIsAddress,
				KIntContactHintIsAdditionalName, 
				KIntContactHintIsSuffixName, 
				KIntContactHintIsPrefixName,
				KIntContactHintIsPronunciation, 
				KIntContactHintIsEmail, 
				KIntContactHintStorageInline,
				KIntContactHintIsCompanyNamePronunciation, 
				KIntContactHintIsGivenNamePronunciation,
				KIntContactHintIsFamilyNamePronunciation
				};
	}
}
