#include <Windows.h>

#include <stdio.h>
#include <ctype.h>

#include "obfuscation/mac2byte.h"
#include "obfuscation/common.h"


// =======  Entrypoint  ==================================================== //

DWORD EthernetStringToAddress(
	IN PCSTR S,
	OUT PCSTR *Terminator,
	OUT PBYTE Addr // 6 bytes
) {
	for (int i = 0; i < 6; i++) {
		DWORD status;
		if ((status = GetByteFromString(S, FALSE, &S, &Addr[i])) != ERROR_SUCCESS)
			return status;

		if (*S == '\0')
			break;
		if (*S == ':' || *S == '-' || *S == '.')
			S++;
	}

	if (Terminator) *Terminator = S;
	return ERROR_SUCCESS;
}