# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within Metanoia-QA, please report it responsibly.

### Disclosure Policy

- **Do not** create a public GitHub issue for security vulnerabilities
- Send a detailed description of the vulnerability to security@metanoia-qa.dev
- Include the following in your report:
  - Type of vulnerability
  - Full paths of source file(s) related to the vulnerability
  - Location of the affected source code
  - Step-by-step instructions to reproduce the issue
  - Proof-of-concept or exploit code (if possible)
  - Impact assessment

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 7 days
- **Resolution**: Within 90 days (depending on severity)

### Security Updates

Security updates will be released as patch versions and announced via:
- GitHub Security Advisories
- Project changelog

## Security Best Practices

When using Metanoia-QA in production:

1. **API Keys**: Never commit `GEMINI_API_KEY` or `SUPABASE_SERVICE_KEY` to version control
2. **Database Connections**: Use TLS for all database connections in production
3. **Network Segmentation**: Isolate the knowledge base from public networks
4. **Access Control**: Implement least-privilege access for agent operations
5. **Audit Logging**: Enable comprehensive logging for compliance tracking
