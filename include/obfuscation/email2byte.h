#pragma once

#include <Windows.h>

#ifndef EMAIL2BYTE_H
#define EMAIL2BYTE_H


/*
Converts an email address from its string representation to its binary form
using the lookup table-based conversion.

Params:
	S:			 Pointer to a null-terminated email address string
	Terminator:  Pointer to the character that terminated the converted string
	Addr:		 A pointer to a 6-byte buffer containing the binary representation
				 of the email address
*/
DWORD EmailStringToBytes(IN PCSTR S, OUT PCSTR *Terminator, OUT PBYTE Addr);


#endif // EMAIL2BYTE_H