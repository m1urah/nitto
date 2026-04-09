# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-09

### Added

- Initial release
- Email-based obfuscation technique (novel method using lookup tables)
- IP (IPv4/IPv6), MAC, and UUID obfuscation techniques
- Encryption support: AES, ChaCha20, RC4, and XOR with multiple modes (ECB, CBC, GCM, etc.)
- Custom C deobfuscation functions to evade EDR monitoring
- Python transformation module for payload obfuscation and encryption
- C sample app demonstrating all 4 obfuscation techniques
- PyInstaller support for bundled executable
