#
# Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description:
#

from cone.public import exceptions


# ============================================================================
# Writer exceptions
# ============================================================================

class HcrWriterError(exceptions.ConeException):
    pass

class DuplicateRecordError(HcrWriterError):
    pass

class ValueNotInRangeError(HcrWriterError):
    pass

class TooLargeLsdDataError(HcrWriterError):
    pass

# ============================================================================
# Reader exceptions
# ============================================================================

class HcrReaderError(exceptions.ParseError):
    pass

class InvalidHcrDataSizeError(HcrReaderError):
    pass

class InvalidHcrHeaderError(HcrReaderError):
    pass

class InvalidLsdSectionOffsetError(HcrReaderError):
    pass

class NoVersionInRepositoryError(HcrReaderError):
    pass

class NoReadOnlyAttributeInRepositoryError(HcrReaderError):
    pass


class InvalidRecordLsdPositionError(HcrReaderError):
    pass

class InvalidRecordValueTypeError(HcrReaderError):
    pass



# ============================================================================
# HCRML parser exceptions
# ============================================================================

class HcrmlParserError(exceptions.ParseError):
    pass

class NoCategoryUIDInHcrmlFileError(HcrmlParserError):
    pass

class NoRefInHcrmlFileError(HcrmlParserError):
    pass

class NoTypeAttributeInSettingHcrmlFileError(HcrmlParserError):
    pass

class NoCategoryNameInHcrmlFileError(HcrmlParserError):
    pass

class NoNameAttributeInSettingHcrmlFileError(HcrmlParserError):
    pass

class NoIdAttributeInSettingHcrmlFileError(HcrmlParserError):
    pass

class NoTypeDefinedInOutPutTagError(HcrmlParserError):
    pass

class InvalidTypeDefinedInOutPutTagError(HcrmlParserError):
    pass

class NoCategoryNameDefinedInCategoryTagError(HcrmlParserError):
    pass

class NoCategoryUidDefinedInCategoryTagError(HcrmlParserError):
    pass

