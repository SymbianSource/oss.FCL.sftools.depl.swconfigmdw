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

public enum ContactHint implements IHint {

    MAILABLE((short) 0x01), 
    SMSABLE((short) 0x02),
    LAND_LINE((short) 0x04), 
    FAXABLE((short) 0x08), 
    PHONABLE((short) 0x10), 
    WORK((short) 0x20), 
    HOME((short) 0x40),
    RING_TONE((short) 0x80), 
    
    VOICE_DIAL((short) 0x0100), //Not used in OS 
    IM_ADDRESS((short) 0x0200), 
    WIRELESS_VILLAGE((short) 0x0400),
    
    /* Modified to reflect auto shifting mistake in spec.
     * The values provided in OS source are applied to the
     * Hint int as if the extension field is combined */
    FILT1((short) 0x008),
	FILT2((short) 0x010),
	FILT3((short) 0x020),
	FILT4((short) 0x040);
    
    
    private short _value;
        
	private ContactHint(short value) {
		_value = value;
	}
    
	public short getValue(){
		return _value;
	}
	
	public static ContactHint[] dbmsValues() {
		return new ContactHint[]{MAILABLE,SMSABLE,LAND_LINE,FAXABLE,PHONABLE,WORK,HOME,RING_TONE};
	}
	
	public static ContactHint[] dbmsExtValues() {
		return new ContactHint[]{VOICE_DIAL,IM_ADDRESS,WIRELESS_VILLAGE,FILT1,FILT2,FILT3,FILT4};
	}
	
	public static ContactHint[] sqliteValues() {
		return new ContactHint[]{MAILABLE,SMSABLE,LAND_LINE,FAXABLE,PHONABLE,WORK,HOME,RING_TONE,VOICE_DIAL,IM_ADDRESS,WIRELESS_VILLAGE};
	}
	
}
