// Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
// All rights reserved.
// This component and the accompanying materials are made available
// under the terms of the License "Symbian Foundation License v1.0"
// which accompanies this distribution, and is available
// at the URL "http://www.symbianfoundation.org/legal/sfl-v10.html".
//
// Initial Contributors:
// Nokia Corporation - initial contribution.
//
// Contributors:
//
// Description:
// RSS.g
//

grammar RSS;
options {backtrack=true; memoize=true;}

@lexer::header {
package com.symbian.sdb.resource;
}

@lexer::members {
  List<RecognitionException> exceptions = new ArrayList<RecognitionException>();

  public List<RecognitionException> getExceptions() {
    return exceptions;
}

  @Override
  public void reportError(RecognitionException e) {
    super.reportError(e);
    exceptions.add(e);
  }
  
  @Override
  public void emitErrorMessage(String arg0) {
  }
}
 
@header {
package com.symbian.sdb.resource;

import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Set;

import com.symbian.sdb.contacts.template.Field;
import com.symbian.sdb.contacts.template.FieldContainer;
import com.symbian.sdb.contacts.template.Flag;
}

@members {

  List<RecognitionException> exceptions = new ArrayList<RecognitionException>();

  public List<RecognitionException> getExceptions() {
    return exceptions;
  }

  @Override
  public void reportError(RecognitionException e) {
    super.reportError(e);
    exceptions.add(e);
  }
  
  @Override
  public void emitErrorMessage(String arg0) {
  }

 	FieldContainer container = new FieldContainer();
    	Field field = new Field();
   
        // private Set<String> set = new HashSet<String>();
         private Integer index = 0;
         
         public void displayRecognitionError(){
         }
         
         public FieldContainer getContainer() {
             return container;
         }
                
             // field type mapping         
             protected HashMap<String, String> fieldTypeMapping = new HashMap<String, String>();
             // mapping for category field      
             protected HashMap<String, String> categoryMapping = new HashMap<String, String>();    
             // mapping for storage field      
             protected HashMap<String, String> storageMapping = new HashMap<String, String>();    
             // mapping for flag field
             protected HashMap<String, String> flagMapping = new HashMap<String, String>();    
     
             public void setFieldTypeMapping(HashMap<String, String> m)  {
                 fieldTypeMapping = m;
             }         
                      
             public void setCategoryMapping(HashMap<String, String> m)  {
                 categoryMapping = m;
             }
             
             public void setStorageMapping(HashMap<String, String> m)  {
                 storageMapping = m;
             }     
                      
             public void setFlagMapping(HashMap<String, String> m)  {
                 flagMapping = m;
             } 
         
         
         // private methods 
         private String resolveMapping(String value, HashMap<String, String> map) {
        	 String resolved = map.get(value);
        	 if (resolved != null) {
        		 return resolved;
        	 }	else {
        		 return value;
        	 }
         }
}


document 
	:	( defineDeclaration | resourceDeclaration )*;

defineDeclaration
	:	'#define' Identifier literal { 
	//TODO add this to the field mapping thing?
	};

literal :	 (HexLiteral | DecimalLiteral)?;
	
resourceDeclaration
	:	'RESOURCE' (arrayDeclaration | rssDeclaration);
	
rssDeclaration
	:	'RSS_SIGNATURE' '{' '}' 	;	
	
arrayDeclaration
	:	'ARRAY' 'r_cntui_new_field_defns' '{' itemsDeclaration ';' '}' ;
	
itemsDeclaration
	:	'items' '=' '{' ( options {greedy=false;} : fieldDeclaration* ) '}'  { };

fieldDeclaration
	:	'FIELD' ( '{' fields* '}' ','? )* { 

            		field.setIndex(index);
              		index++;
              	     
              	     	container.add(field.getVCardMapping(), field);
              	     	field = new Field();  		
	}	;
	
fields	:	(flags | category | fieldStorageType | contactFieldType | vCardMappingField | extraMapping | fieldName | other ) ';' ;


fieldsdef 
	:	Identifier ( '|' fieldsdef )* { 
		//set.add($Identifier.text); 
		};
		
other 	:	Identifier '=' fieldsdef	{  
		//addSetFieldMember($Identifier.text);
		} ;

flags	:	'flags' '=' flagsdef {
		//addSetFieldMember("flags");		
		};

flagsdef 
	:	Identifier ( '|' flagsdef )* { 		
	        String value = $Identifier.text;
                        String flag = resolveMapping(value, flagMapping);
                            	
            			int result;
            			if (flag.startsWith("0x")) {
            				result = Integer.parseInt(flag.replace("0x", ""), 16);
            			} else {
            				result = Integer.parseInt(flag);
            			}
            			Flag f = new Flag(value, result);
                    	
                    	field.addFlag(f);
		};

extraMapping
	:	'extraMapping' '=' '{' ( mapping )* '}'  {  
		//addSetFieldMember("extraMapping");
	}  ;
	
mapping	:	'MAPPING' '{' 'mapping' '=' Identifier ';' '}' ','? {
              		String value = $Identifier.text; 
              		field.addProperty(value);
	};

category
	:	'category' '=' Identifier {
		String value =  $Identifier.text;
              	String category = resolveMapping(value, categoryMapping);	
              	field.setCategory(category);
		};

contactFieldType
	:	'contactFieldType' '=' Identifier {  
		String value =  $Identifier.text;
              	field.setFieldType(value);
		}	; 

fieldStorageType
	:	'fieldStorageType' '=' Identifier {
		//storageMapping
		 String value = $Identifier.text;
              	 String storage = resolveMapping(value, storageMapping);
              	 field.setStorageType(storage);
		} ;

vCardMappingField
	:	'vCardMapping' '=' Identifier  { 
              		String value = $Identifier.text;
			field.setVCardMapping(value);       
		};

fieldName
	:	'fieldName' '=' Identifier  { 
              		String value = $Identifier.text;
			field.setFieldName(value);      
		};


// LEXER


HexLiteral : '0' ('x'|'X') HexDigit+ IntegerTypeSuffix? ;

DecimalLiteral : ('0' | '1'..'9' '0'..'9'*) IntegerTypeSuffix? ;

fragment
HexDigit : ('0'..'9'|'a'..'f'|'A'..'F') ;

fragment
IntegerTypeSuffix : ('l'|'L') ;

Identifier 
    :   Letter (Letter|JavaIDDigit)*
    ;

fragment
Letter
    :  '\u0024' |
       '\u0041'..'\u005a' |
       '\u005f' |
       '\u0061'..'\u007a' |
       '\u00c0'..'\u00d6' |
       '\u00d8'..'\u00f6' |
       '\u00f8'..'\u00ff' |
       '\u0100'..'\u1fff' |
       '\u3040'..'\u318f' |
       '\u3300'..'\u337f' |
       '\u3400'..'\u3d2d' |
       '\u4e00'..'\u9fff' |
       '\uf900'..'\ufaff'
    ;

fragment
JavaIDDigit
    :  '\u0030'..'\u0039' |
       '\u0660'..'\u0669' |
       '\u06f0'..'\u06f9' |
       '\u0966'..'\u096f' |
       '\u09e6'..'\u09ef' |
       '\u0a66'..'\u0a6f' |
       '\u0ae6'..'\u0aef' |
       '\u0b66'..'\u0b6f' |
       '\u0be7'..'\u0bef' |
       '\u0c66'..'\u0c6f' |
       '\u0ce6'..'\u0cef' |
       '\u0d66'..'\u0d6f' |
       '\u0e50'..'\u0e59' |
       '\u0ed0'..'\u0ed9' |
       '\u1040'..'\u1049'
   ;

WS  :  (' '|'\r'|'\t'|'\u000C'|'\n') {$channel=HIDDEN;}
    ;

COMMENT
    :   '/*' ( options {greedy=false;} : . )* '*/' {$channel=HIDDEN;} ;

LINE_COMMENT
    : '//' ~('\n'|'\r')* '\r'? '\n' {$channel=HIDDEN;} ;
    
INCLUDE 
	: '#include' ~('\n'|'\r')* '\r'? '\n' {$channel=HIDDEN;} ;

STRUCT	:	'STRUCT' ( options {greedy=false;} : . )* '}' {$channel=HIDDEN;} ;	

IF_STM
    : '#if' ~('\n'|'\r')* '\r'? '\n' {$channel=HIDDEN;} ;
    
ENDIF_STM
    : '#endif' ~('\n'|'\r')* '\r'? '\n' {$channel=HIDDEN;} ;
    
    
    
