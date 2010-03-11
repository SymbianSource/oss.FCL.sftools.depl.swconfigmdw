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

package com.symbian.sdb.configuration;

import java.text.MessageFormat;

public enum DocumentVersion {
    V10("//{0}"),
    V20("//database[@type=\"{1}\"]/{0} | //common/applicable[@type=\"{1}\"]/following-sibling::database/{0}");
    
    private DocumentVersion(String query) {
        this.query = query;
    }
    
    private String query;
    
    public String getQuery(Object[] values) {
        return MessageFormat.format(query, values);
    }
    
}
