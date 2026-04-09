#pragma once

#include <Windows.h>

#ifndef UUID2BYTE_H
#define UUID2BYTE_H


/*
Custom implementation of the UuidFromStringA function. Converts a UUID or GUID
from its string representation to its binary form.

The input must represent a valid 36-character alphanumeric string encoded as hex
digits (0-9, A-F) separated by hyphens (-).

Params:
	S:			 Pointer to a null-terminated MAC string
	IsGuid:		 Wether the string represents a GUID
	Terminator:  Pointer to the character that terminated the converted string
	Addr:		 A pointer to a 16-byte buffer containing the binary
				 representation of the UUID
*/
DWORD UUIDFromString(IN PCSTR S, IN BOOL IsGUID, OUT PCSTR *Terminator, OUT PBYTE Addr);


#endif // UUID2BYTE_H
