#pragma once

#include <Windows.h>

#ifndef MAC2BYTE_H
#define MAC2BYTE_H


/*
Custom implementation of the RtlEthernetStringToAddressA function. Converts a
MAC address from its string representation to its binary form.

The input must represent a 6-byte MAC address encoded as hex digits (0-9, A-F). The
address may optionally include the following separators: colons (:), hyphens (-),
or dots (.). Parsing is case-insensitive.

Supported formats:

- UNIX (colons): 00:1A:2B:3C:4D:5E
- Windows (hyphens): 00-1A-2B-3C-4D-5E
- Network equipment, like Cisco (periods): 001A.2B3C.4D5E
- No separator: 001A2B3C4D5E

Params:
	S:			 Pointer to a null-terminated MAC string
	Terminator:  Pointer to the character that terminated the converted string
	Addr:		 A pointer to a 6-byte buffer containing the binary
				 representation of the MAC address
*/
DWORD EthernetStringToAddress(IN PCSTR S, OUT PCSTR *Terminator, OUT PBYTE Addr);


#endif // MAC2BYTE_H