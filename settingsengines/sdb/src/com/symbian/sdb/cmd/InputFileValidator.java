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

import java.io.File;
import java.io.FileFilter;
import java.util.List;
import java.util.ListIterator;

import org.apache.commons.cli2.validation.InvalidArgumentException;
import org.apache.commons.cli2.validation.Validator;

public class InputFileValidator implements Validator {
    
	private boolean supportsWildcards = false;
	private boolean mustExist = false;
	
	private InputFileValidator() {
	}
	
	public void validate(List values) throws InvalidArgumentException {
    	if (supportsWildcards) {
    		validateWithWildcards(values);
    	}
    	else {
    		validateWithoutWildcards(values);
    	}
    }
	
    @SuppressWarnings("unchecked")  
    private void validateWithoutWildcards(List values) throws InvalidArgumentException {
        for (final ListIterator i = values.listIterator(); i.hasNext();) {
            String input = (String) i.next();
            File file = new File(input);

            if (mustExist && !file.exists()) {
            	throw new InvalidArgumentException(input + " does not exist");
            }

            i.set(file);
        }
    }
    
    @SuppressWarnings("unchecked")
    private void validateWithWildcards(List values) throws InvalidArgumentException {
        for (final ListIterator i = values.listIterator(); i.hasNext();) {
            String input = (String) i.next();
            File file = new File(input);

            if (file.getName().contains("*") || file.getName().contains("?")) {
                File dirFile = file.getParentFile();
                if (dirFile.exists() && dirFile.isDirectory()) {
                    i.remove();
                    String pattern = file.getName().replace("*", ".*").replace("?", ".?");
                    File[] list = getFiles(dirFile, pattern);
                    for (File f : list) {
                        i.add(f);
                    }
                } else {
                    throw new InvalidCmdArgumentException("No matching files found: " + input + " ");
                }
            } else {
                 if (file.exists()) {
                    if (file.isDirectory()) {
                        i.remove();
                        File[] list = getFiles(file, ".*");
                        for (File f : list) {
                            i.add(f);
                        }
                    } else {
                        i.set(file);
                    }
                } else {
                    throw new InvalidCmdArgumentException("Invalid argument: " + input + " not found");
                }
            }
    
        }
    }
    
    private File[] getFiles(File directory, final String pattern) {
        File[] files = directory.listFiles(new FileFilter() {            
            public boolean accept(File filepath) {
                if (filepath.isDirectory()) {
                    return false;
                } else {
                    return filepath.getName().matches(pattern);
                }
            }
        });
        return files;
    }
    
    public static InputFileValidator getInstance() {
    	return new InputFileValidator();
    }
 
    public static InputFileValidator getInstanceForFilesWhichMustExist() {
    	final InputFileValidator ifv = new InputFileValidator();
    	ifv.mustExist = true;
    	return ifv;
    }
    
    public static InputFileValidator getInstanceForPathsWithWildcardSupport() {
    	final InputFileValidator ifv = new InputFileValidator();
    	ifv.supportsWildcards = true;
    	return ifv;
    }
}
