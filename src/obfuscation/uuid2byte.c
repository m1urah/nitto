#include <Windows.h>

#include <stdio.h>
#include <ctype.h>
#include <stdint.h>

#include "obfuscation/common.h"


// =======  Entrypoint  ==================================================== //

DWORD UUIDFromString(
	IN PCSTR S,
	IN BOOL IsGUID,
	OUT PCSTR* Terminator,
	OUT PBYTE Addr // 16 bytes
) {
	for (int i = 0; i < 16; i++) {
		DWORD status;
		if ((status = GetByteFromString(S, FALSE, &S, &Addr[i])) != ERROR_SUCCESS)
			return status;

		if (*S == '\0')
			break;
		if (*S == '-')
			S++;
	}

	// Reverse endianess for first 8B
	if (IsGUID) {
		BYTE t;

		// -- Segment 1 --
		t = Addr[0]; Addr[0] = Addr[3]; Addr[3] = t;
		t = Addr[1]; Addr[1] = Addr[2]; Addr[2] = t;

		// -- Segment 2 --
		t = Addr[4]; Addr[4] = Addr[5]; Addr[5] = t;

		// -- Segment 2 --
		t = Addr[6]; Addr[6] = Addr[7]; Addr[7] = t;
	}

	if (Terminator) *Terminator = S;
	return ERROR_SUCCESS;
}