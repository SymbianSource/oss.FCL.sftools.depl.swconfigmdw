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

package com.symbian.sdb.contacts.importer.vcard;

/**
 * @author krzysztofZielinski
 *
 */
public enum StructurecFieldTemplateFieldIDs {

    FIRST_NAME("KUidContactFieldGivenNameValue"), LAST_NAME("KUidContactFieldFamilyNameValue"), NAME_PREFIX("KUidContactFieldPrefixNameValue"), ADDITIONAL_NAME("KUidContactFieldAdditionalNameValue"), NAME_SUFFIX("KUidContactFieldSuffixNameValue"); // NAME_SUFFIX() 

    private String value;
    
    private StructurecFieldTemplateFieldIDs(String value) {
        this.value = value;
    }
    
    public String getValue()   {
        return this.value;
    }
    
}
