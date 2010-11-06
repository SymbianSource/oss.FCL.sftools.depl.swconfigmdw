#ifndef MULTI_HEADER_H
#define MULTI_HEADER_H

#include <hcr.h>

const HCR::TCategoryUid KTest1Category = 0x10001234;

const HCR::TElementId KInt8Setting       = 0x00000000;
// Test setting 2
const HCR::TElementId KUint32Setting     = 0x00000001;
const HCR::TElementId KInt32ArraySetting = 0x00000002;
const HCR::TElementId KBinDataSetting    = 0x00000003;

// ----------------------------------------------------------------------

const HCR::TCategoryUid KTest2Category = 0x20001234;

const HCR::TElementId KLinAddrSetting     = 0x00000000;
const HCR::TElementId KInt64Setting       = 0x00000001;
const HCR::TElementId KUint32ArraySetting = 0x00000002;
const HCR::TElementId KText8Setting       = 0x00000003;

// ----------------------------------------------------------------------

const HCR::TCategoryUid KTest3Category = 0x30001234;

const HCR::TElementId KBoolSetting = 0x00000000;

#endif