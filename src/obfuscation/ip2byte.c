#include <Windows.h>

#include "obfuscation/ip2byte.h"


// =======  IPv6  ========================================================== //

static DWORD ParseIpv6Component(
	IN PCSTR S,
	OUT PCSTR *Terminator,
	OUT PINT segment
) {
	int s = 0;
	int digits = 0;

	while (1) {
		UCHAR c = *S;
		int value;

		if (c == ':' || c == '\0') {
			if (digits == 0) goto error;
			*segment = s;
			*Terminator = S;
			return ERROR_SUCCESS;
		}

		if (c >= '0' && c <= '9')
			value = c - '0';
		else if (c >= 'A' && c <= 'F')
			value = c - 'A' + 10;
		else if (c >= 'a' && c <= 'f')
			value = c - 'a' + 10;
		else
			goto error;

		if (digits == 4) goto error;

		s = (s * 16) + value;
		digits++;

		S++;
	}

error:
	if (Terminator) *Terminator = S;
	return ERROR_INVALID_PARAMETER;
}

// IPv4-embedded IPv6 not supported yet
DWORD Ipv6StringToAddress(
	IN PCSTR S,
	OUT PCSTR *Terminator,
	OUT PBYTE Addr // 16 bytes
) {
	int nBytes = 0;
	int segment = 0;
	BOOL compressedFound = 0;
	BYTE afterCompressed[7 * 2] = { 0 }; // Max of 7 segments after ::, e.g. ::1:2:3:4:5:6:7
	SIZE_T afterCompressedLen = 0;

	if (S[0] == '\0') goto error;
	if (S[0] == ':') {
		if (S[1] != ':') goto error;
		S++; S++;
		Addr[0] = (unsigned char)0;
		Addr[1] = (unsigned char)0;
		nBytes = 2;
		compressedFound = TRUE;
	}

	while (1) {
		if (*S == '\0') {
			if (afterCompressedLen + nBytes > BYTE_SIZE_IPV6) goto error;

			if (*Terminator) *Terminator = S;
			break;
		}

		if (ParseIpv6Component(S, Terminator, &segment) != 0x00) goto error;

		// Split the segment into its 2 bytes
		UCHAR byte1, byte2;
		byte1 = (UCHAR)(segment >> 8);
		byte2 = (UCHAR)(segment & 0xFF);

		if (compressedFound) {
			if (afterCompressedLen + 2 > 14) goto error;
			afterCompressed[afterCompressedLen++] = byte1;
			afterCompressed[afterCompressedLen++] = byte2;
		}
		else {
			if (nBytes + 2 > BYTE_SIZE_IPV6) goto error;
			Addr[nBytes++] = byte1;
			Addr[nBytes++] = byte2;
		}

		if (afterCompressedLen + nBytes > BYTE_SIZE_IPV6) goto error;

		S = *Terminator;
		char c = *S;

		if (c == ':') {
			if (S[1] == ':') {
				if (compressedFound) goto error;
				compressedFound = TRUE;
				S++;
			}
			else if (S[1] == '\0') goto error;
			S++;
		}
	}

	SIZE_T missingBytes = BYTE_SIZE_IPV6 - nBytes - afterCompressedLen;
	if (compressedFound && missingBytes == 0) goto error; // We found ::, but we already reach 16 bytes

	if (!memset(Addr + nBytes, 0, missingBytes)) {
		printf("[-] Error while modifying destination buffer: %d", GetLastError());
		return GetLastError();
	}

	errno_t err;
	if (err = memcpy_s(Addr + nBytes + missingBytes, afterCompressedLen, afterCompressed, afterCompressedLen) != 0) {
		printf("[-] Error while modifying destination buffer (2): %d", err);
		return err;
	}

	return ERROR_SUCCESS;

error:
	if (Terminator) *Terminator = S;
	return ERROR_INVALID_PARAMETER;
}


// =======  IPv4  ========================================================== //

DWORD Ipv4StringToAddress(
	IN PCSTR S,
	IN BOOLEAN Strict,
	OUT PCSTR *Terminator,
	OUT PBYTE Addr // 4 bytes
) {
	if (Strict == FALSE) {
		printf("[-] Error converting IPv4 string to binary address: Strict=FALSE is not supported");
		return ERROR_UNSUPPORTED_TYPE;
	}

	int nBytes = 0;
	int segment = 0;
	while (1) {
		char c = *S;
		if (c == '.' || c == '\0') {
			if (nBytes > 3) return ERROR_INVALID_PARAMETER;

			Addr[nBytes++] = (unsigned char)segment;
			segment = 0;

			if (c == '\0') {
				// An IP must have exactly 4 segments
				if (nBytes != 4) return ERROR_INVALID_PARAMETER;
				break;
			}

			S++; // Move past the dot
			continue;
		}

		if (c < '0' || c > '9') return ERROR_INVALID_PARAMETER;

		// Shift and convert to int
		segment = (segment * 10) + (c - '0');
		if (segment > 255) return ERROR_INVALID_PARAMETER;
		S++;
	}

	*Terminator = S;
	return ERROR_SUCCESS;
}
