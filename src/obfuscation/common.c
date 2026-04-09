#include <Windows.h>

#include "obfuscation/common.h"

DWORD GetByteFromString(
	IN unsigned char* S,
	IN BOOL CaseSensitive,
	OUT unsigned char** Terminator,
	OUT PBYTE Byte
) {
	unsigned char pair[2] = { 0 };
	for (size_t i = 0; i < 2 && *S; i++) {
		char c = *S;
		if (!CaseSensitive)
			c = toupper(c);  // For non a-z, returns the value

		if (c < '0' || (c > '9' && c < 'A') || c > 'F') {
			return ERROR_INVALID_PARAMETER;
		}

		pair[i] = c;
		S++;
	}

	*Byte = (pair[0] <= '9' ? pair[0] - '0' : pair[0] - 'A' + 10) << 4;
	*Byte |= pair[1] <= '9' ? pair[1] - '0' : pair[1] - 'A' + 10;

	if (Terminator) *Terminator = S;
	return ERROR_SUCCESS;
}