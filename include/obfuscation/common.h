#pragma once

#include <Windows.h>

#ifndef COMMON_H
#define COMMON_H


/*
Converts the first two characters of a string to its binary representation.

Params:
	S:				Pointer to a null-terminated string
	CaseSensitive:	Whether the character should be treated as case-sensitive.
	Terminator:		Pointer to the character that terminated the converted string
	Addr:			A pointer to a buffer containing the binary representation of
					the first two characters.
*/
DWORD GetByteFromString(IN unsigned char *S, IN BOOL CaseSensitive, OUT unsigned char **Terminator, OUT PBYTE Byte);


#endif // COMMON_H