#pragma once

#include <Windows.h>

#ifndef IP2BYTE_H
#define IP2BYTE_H

#define BYTE_SIZE_IPV4 4
#define BYTE_SIZE_IPV6 16


/*
Custom implementation of the RtlIpv6StringToAddressA function. Converts an
IPv6 address from its string representation to its binary form.

Params:
	S:			 Pointer to a null-terminated IPv6 string
	Terminator:  Pointer to the character that terminated the converted string
	segment:	 A pointer to a 16-byte buffer containing the binary
				 representation of the IPv6 address
*/
DWORD Ipv6StringToAddress(IN PCSTR S, OUT PCSTR *Terminator, OUT PBYTE Addr);

/*
Custom implementation of the RtlIpv4StringToAddressA function. Converts an
IPv4 address from its string representation to its binary form.

Params:
	S:			 Pointer to a null-terminated IPv4 string
	Strict:		 Wether the string must be four-part dotted-decimal notation, or
				 allow legacy forms (3-, 2-, and 1-part) and formats (hex and
				 octal components).
	Terminator:  Pointer to the character that terminated the converted string
	segment:	 A pointer to a 16-byte buffer containing the binary
				 representation of the IPv4 address
*/
DWORD Ipv4StringToAddress(IN PCSTR S, IN BOOLEAN Strict, OUT PCSTR *Terminator, OUT PBYTE Addr);


#endif // IP2BYTE_H