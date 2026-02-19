# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email the maintainers with details of the vulnerability
3. Include steps to reproduce if possible
4. Allow reasonable time for a fix before public disclosure

## Security Considerations

- QMeter Analyzer processes XML files which may contain sensitive infrastructure information
- Reports may include machine names, IP addresses, and hardware configurations
- Ensure output files are stored securely and access-controlled
- The tool does not transmit any data externally
- All processing is done locally
