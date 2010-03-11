CREATE TABLE CONTACTS(CM_Id INTEGER NOT NULL AUTOINCREMENT, CM_Type INTEGER, CM_PrefTemplateRefId INTEGER, CM_UIDString CHAR(244), CM_Last_modified TIMESTAMP, CM_ContactCreationDate TIMESTAMP, CM_Attributes UNSIGNED INTEGER, CM_ReplicationCount UNSIGNED INTEGER, CM_Header LONG VARBINARY, CM_TextBlob LONG VARBINARY, CM_SearchableText LONG VARCHAR);
CREATE UNIQUE INDEX cnt_id_index ON CONTACTS(CM_Id) COLLATE NORMAL;
CREATE TABLE IDENTITYTABLE(Parent_CMID INTEGER, CM_FirstName CHAR(255), CM_LastName CHAR(255), CM_CompanyName CHAR(255), CM_Type INTEGER, CM_Attributes UNSIGNED INTEGER, CM_HintField TINYINT, CM_ExtHintField UNSIGNED SMALLINT, CM_FirstNmPrn CHAR(255), CM_LastNmPrn CHAR(255), CM_CompanyNmPrn CHAR(255));
CREATE UNIQUE INDEX IdentityIdIndex ON IDENTITYTABLE(Parent_CMID) COLLATE NORMAL;
CREATE TABLE EMAILTABLE(EMail_FieldID INTEGER NOT NULL AUTOINCREMENT, EmailParent_CMID INTEGER, EMailAddress CHAR(255));
CREATE UNIQUE INDEX EmailIdentityIdIndex ON EMAILTABLE( EMail_FieldID, EmailParent_CMID) COLLATE NORMAL;
CREATE TABLE PHONE(CM_Id INTEGER NOT NULL, CM_PhoneMatching INTEGER NOT NULL, CM_ExtendedPhoneMatching INTEGER NOT NULL);
CREATE UNIQUE INDEX cnt_phone_index ON PHONE( CM_PhoneMatching, CM_Id ) COLLATE NORMAL;
CREATE TABLE GROUPS(CM_Id INTEGER NOT NULL, CM_Members INTEGER NOT NULL);
CREATE INDEX cnt_group_index ON GROUPS( CM_Members, CM_Id ) COLLATE NORMAL;      
CREATE TABLE GROUPS2(CM_Id INTEGER NOT NULL, CM_GroupMembers LONG VARBINARY);
CREATE UNIQUE INDEX cnt_group_index2 ON GROUPS2(CM_Id) COLLATE NORMAL;
CREATE TABLE PREFERENCES(CM_PrefFileId SMALLINT, CM_PrefTemplateId INTEGER, CM_PrefOwnCardId INTEGER, CM_PrefCardTemplatePrefId INTEGER, CM_PrefCardTemplateId LONG VARBINARY, CM_PrefGroupIdList LONG VARBINARY, CM_PrefFileVer INTEGER, CM_creationdate TIMESTAMP, CM_MachineUID BIGINT, CM_PrefSortOrder LONG VARBINARY);
CREATE TABLE SYNC(CM_Id UNSIGNED INTEGER NOT NULL AUTOINCREMENT, CM_LastSyncDate TIMESTAMP);
CREATE UNIQUE INDEX sync_id_index ON SYNC(CM_Id) COLLATE NORMAL;
