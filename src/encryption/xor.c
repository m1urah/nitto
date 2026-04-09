#include <Windows.h>
#include <stdint.h>

#include "encryption/xor.h"

void XORDecrypt(
	IN const uint8_t *key,
	IN const size_t keyLen,
	IN const void *cipherText,
	IN const size_t cipherTextLen,
	OUT void *plainText
) {
	const uint8_t* keyPtr = key;
	for (size_t i = 0; i < cipherTextLen; i++) {
		if (i != 0 && i % keyLen == 0)
			keyPtr = key;

		((uint8_t*)plainText)[i] = ((uint8_t*)cipherText)[i] ^ *keyPtr;
		keyPtr++;
	}
}