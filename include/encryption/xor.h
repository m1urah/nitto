#pragma once

#ifndef XOR_H
#define XOR_H

/*
Decrypts a given plaintext using the given key. Each byte of the plaintext is
XORed against the key, which wraps around once it reaches the end.

For example, if the key is 'abcd' and len(plaintext) = 9, the key will end up
being: abcdabcda.

IMPORTANT! If key or cipherText are initilized as hexadecimal string literals
(e.g. "\xFF\x0C"), the length parameters must NOT include the NULL terminator.
Beware of sizeof on string literals, it includes the trailing \0 byte.

Params:
	key:		    A byte array representing the key
	keyLen:         The length of the key arr
	cipherText:	    An array containing the ciphertext
    cipherTextLen:	The length of the ciphertext
    plainText:      A pointer to a buffer containing the plaintext bytes
*/
void XORDecrypt(
    IN const uint8_t *key, IN const size_t keyLen, IN const void *cipherText,
    IN const size_t cipherTextLen, OUT void *plainText
);


#endif // XOR_H
