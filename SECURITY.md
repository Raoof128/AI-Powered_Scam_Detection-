# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for
receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of the AI-Powered Scam Detection Platform seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **your.email@example.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

* Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
* Full paths of source file(s) related to the manifestation of the issue
* The location of the affected source code (tag/branch/commit or direct URL)
* Any special configuration required to reproduce the issue
* Step-by-step instructions to reproduce the issue
* Proof-of-concept or exploit code (if possible)
* Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

### Preferred Languages

We prefer all communications to be in English.

## Security Best Practices

### For Users

1. **API Keys**: Never commit API keys or credentials to version control
2. **Environment Variables**: Always use environment variables for sensitive data
3. **HTTPS**: Use HTTPS in production environments
4. **Updates**: Keep the platform and dependencies up to date
5. **Access Control**: Implement proper authentication and authorization

### For Contributors

1. **Dependencies**: Regularly update dependencies to patch vulnerabilities
2. **Secrets**: Use `.env` files (gitignored) for local secrets
3. **Code Review**: All code changes should be reviewed before merging
4. **Testing**: Include security tests in test suite
5. **Static Analysis**: Run security scanners (bandit, safety) before commits

## Known Security Considerations

### Input Validation

All API endpoints use Pydantic for input validation to prevent:
- SQL injection (via parameterized queries)
- XSS attacks (via sanitized outputs)
- Command injection
- Path traversal

### Authentication

- API key authentication via `X-API-Key` header
- Keys are stored hashed (bcrypt) in database
- Rate limiting per API key (configurable)
- Key expiration support

### Data Privacy

- No PII is stored without explicit consent
- Database connections use SSL/TLS
- Passwords hashed with bcrypt
- GDPR-compliant data retention policies

### Network Security

- CORS configuration for API access control
- Request size limits (1MB default)
- Timeout configurations (30s default)
- Rate limiting (100 req/min per key)

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.1) and documented in [CHANGELOG.md](CHANGELOG.md).

Critical security updates will be:
1. Released within 48 hours of confirmation
2. Announced via GitHub Security Advisories
3. Documented with CVE numbers when applicable
4. Backported to supported versions

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported versions
4. Release patches as soon as possible

We ask that you:
- Give us reasonable time to fix the issue before public disclosure
- Make a good faith effort to avoid privacy violations, data destruction, and service disruption
- Do not access or modify data that doesn't belong to you

## Bug Bounty Program

Currently, we do not have a bug bounty program. However, we deeply appreciate security researchers who help us keep our platform secure.

## Security Tools Used

- **bandit**: Python security linter
- **safety**: Dependency vulnerability scanner
- **CodeQL**: Code security analysis (GitHub Actions)
- **Dependabot**: Automated dependency updates
- **pre-commit hooks**: Automated security checks

## Contact

For security-related questions or concerns, please contact:
- **Email**: your.email@example.com
- **PGP Key**: [Link to PGP key if applicable]

## Acknowledgments

We thank the following security researchers for responsibly disclosing vulnerabilities:

- None reported yet

---

This security policy is inspired by the [GitHub Security Lab](https://securitylab.github.com/) and follows industry best practices.
