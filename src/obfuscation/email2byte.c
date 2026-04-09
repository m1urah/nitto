#include <Windows.h>

#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "obfuscation/email2byte.h"
#include "hashTables/firstNames.h"
#include "hashTables/lastNames.h"
#include "hashTables/others.h"


// =======  Constants  ===================================================== //

#define FIRST_NAMES_COUNT		4096
#define LAST_NAMES_COUNT		4096
#define MAX_EMAIL_SIZE			60
#define MAX_ELEMENT_SIZE		21

#define EMAIL_EL_PARTS_COUNT	6

#define MAX_IDX_FIRST			0xFFF  // 12
#define MAX_IDX_MIDDLE			0x1F   // 5
#define MAX_IDX_LAST			0xFFF  // 12
#define MAX_IDX_NUMBER			0x1FF  // 9
#define MAX_IDX_DOMAIN			0x1F   // 5
#define MAX_IDX_TLD				0x1F   // 5


// =======  Helpers  ======================================================= //

static DWORD GetElementByDelimiter(
	IN PCSTR S,
	IN PCSTR Delimiters,
	OUT PCSTR *Terminator,
	OUT PCHAR *Element,
	OUT PWORD ElementSize
) {
	char *delPointer = NULL;
	if (Delimiters == NULL || Delimiters[0] == '\0') {
		delPointer = (char *)(S + strlen(S));
	} else {
		delPointer = strpbrk(S, Delimiters);
	}
	if (delPointer == NULL) return ERROR_INVALID_PARAMETER;

	*ElementSize = (WORD)(delPointer - S);
	if (*ElementSize > MAX_ELEMENT_SIZE) return ERROR_INVALID_PARAMETER;

	*Element = (PCHAR)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, (*ElementSize + 1) * sizeof(char));
	if (*Element == NULL) {
		return ERROR_OUTOFMEMORY;
	}

	memcpy(*Element, S, *ElementSize);
	(*Element)[*ElementSize] = '\0';

	if (Terminator) *Terminator = delPointer;
	return ERROR_SUCCESS;
}


// =======  Entrypoint  ==================================================== //

DWORD EmailStringToBytes(
	IN PCSTR S,
	OUT PCSTR *Terminator,
	OUT PBYTE Addr // 6 bytes
) {
	if (S == NULL || *S == NULL) return ERROR_INVALID_PARAMETER;

	PCHAR Element = NULL;
	WORD ElementSize = 0;
	DWORD status = 0;

	typedef PHASH_TABLE_VALUE (*LOOKUP_FN)(PCHAR, WORD); // All types share the same signature
	typedef struct {
		const char *delimiter;
		WORD max_idx;
		LOOKUP_FN lookup;
		BOOL skip_delim;
	} EMAIL_PART_RULE;

	EMAIL_PART_RULE rules[EMAIL_EL_PARTS_COUNT] = {
		{ ".",			MAX_IDX_FIRST,	 GetFirstName,  TRUE },
		{ ".",			MAX_IDX_MIDDLE,  GetOtherWord,  TRUE },
		{ "0123456789", MAX_IDX_LAST,	 GetLastName,   FALSE },
		{ "@",			MAX_IDX_NUMBER,  NULL,		    TRUE },
		{ ".",			MAX_IDX_DOMAIN,  GetOtherWord,  TRUE },
		{ "\0",			MAX_IDX_TLD,	 GetOtherWord,  FALSE },
	};

	short idxs[6] = { 0 };
	short totalElementSize = 0;
	char *pReadCursor = (char*)S;
	for (size_t i = 0; i < EMAIL_EL_PARTS_COUNT && *pReadCursor; i++) {
		status = GetElementByDelimiter(
			pReadCursor,
			rules[i].delimiter,
			&pReadCursor,
			&Element,
			&ElementSize
		);

		if (status != ERROR_SUCCESS)
			return status;

		if (rules[i].skip_delim)
			pReadCursor++; // Move it past the delimiter

		totalElementSize += ElementSize;
		if (totalElementSize > MAX_EMAIL_SIZE)
			return ERROR_INVALID_PARAMETER;

		if (rules[i].lookup) {
			PHASH_TABLE_VALUE v = rules[i].lookup(Element, ElementSize);
			if (!v) return ERROR_INVALID_PARAMETER;

			idxs[i] = v->idx;
		} else {
			idxs[i] = atoi(Element);
			if (idxs[i] == 0 && strcmp(Element, "0")) return ERROR_INVALID_PARAMETER;
		}

		if (idxs[i] > rules[i].max_idx)
			return ERROR_INVALID_PARAMETER;
	}

	// [first_name].[middle_initial].[last_name][number]@[domain].[tld]
	Addr[0] = (unsigned char)(idxs[0] >> 4);							// 16 - 4 last bits = 12 first
	Addr[1] = (unsigned char)(((idxs[0] & 0xF) << 4) | (idxs[1] >> 1)); // idxs[1] < 32 (2^5)
	Addr[2] = (unsigned char)(((idxs[1] & 1) << 7) | (idxs[2] >> 5));
	Addr[3] = (unsigned char)(((idxs[2] & 0x1F) << 3) | (idxs[3] >> 6));
	Addr[4] = (unsigned char)(((idxs[3] & 0x3F) << 2) | (idxs[4] >> 3));
	Addr[5] = (unsigned char)(((idxs[4] & 7) << 5) | idxs[5]);

	if (Terminator) *Terminator = *pReadCursor;
	return ERROR_SUCCESS;
}
