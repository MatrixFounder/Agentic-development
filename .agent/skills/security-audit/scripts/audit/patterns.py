"""
Regex pattern definitions for security scanning.

All patterns include CWE identifiers for compliance integration.
Known Limitation: regex-only (no AST parsing). Will match inside comments,
docstrings, and string literals. Always manually verify findings.
"""

# --- Secret Patterns ---
# Format: (regex, name, severity, cwe_id)
SECRET_PATTERNS = [
    # API Keys & Tokens
    (r'api[_-]?key\s*[=:]\s*["\'][^"\']{10,}["\']', "API Key", "high", "CWE-798"),
    (r'token\s*[=:]\s*["\'][^"\']{10,}["\']', "Token", "high", "CWE-798"),
    (r'bearer\s+[a-zA-Z0-9\-_.]+', "Bearer Token", "critical", "CWE-798"),

    # Cloud Credentials
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key", "critical", "CWE-798"),
    (r'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\'][^"\']+["\']', "AWS Secret", "critical", "CWE-798"),
    (r'AZURE[_-]?[A-Z_]+\s*[=:]\s*["\'][^"\']+["\']', "Azure Credential", "critical", "CWE-798"),
    (r'GOOGLE[_-]?[A-Z_]+\s*[=:]\s*["\'][^"\']+["\']', "GCP Credential", "critical", "CWE-798"),

    # Database & Connections
    (r'password\s*[=:]\s*["\'][^"\']{4,}["\']', "Password", "high", "CWE-259"),
    (r'(mongodb|postgres|mysql|redis):\/\/[^\s"\']+', "Database Connection String", "critical", "CWE-798"),

    # Private Keys
    (r'-----BEGIN\s+(RSA|PRIVATE|EC|DSA|OPENSSH)\s+KEY-----', "Private Key", "critical", "CWE-321"),
    (r'ssh-rsa\s+[A-Za-z0-9+/]+', "SSH Key", "critical", "CWE-321"),
    (r'(?:private[_-]?key|secret[_-]?key|signing[_-]?key)\s*[=:]\s*["\']?0x[a-fA-F0-9]{64}\b',
     "Private Key (Hex)", "critical", "CWE-321"),

    # JWT
    (r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+', "JWT Token", "high", "CWE-798"),

    # GitHub Tokens (ghp_, gho_, ghu_, ghs_, ghr_)
    (r'gh[pousr]_[A-Za-z0-9_]{36,}', "GitHub Token", "critical", "CWE-798"),

    # Slack Tokens
    (r'xox[bpoas]-[A-Za-z0-9-]+', "Slack Token", "critical", "CWE-798"),

    # Stripe Keys
    (r'sk_live_[A-Za-z0-9]{20,}', "Stripe Secret Key", "critical", "CWE-798"),
    (r'rk_live_[A-Za-z0-9]{20,}', "Stripe Restricted Key", "critical", "CWE-798"),

    # AI Provider API Keys
    (r'sk-ant-[A-Za-z0-9_-]{20,}', "Anthropic API Key", "critical", "CWE-798"),
    (r'sk-proj-[A-Za-z0-9_-]{20,}', "OpenAI Project Key", "critical", "CWE-798"),
    (r'sk-[A-Za-z0-9]{40,}', "OpenAI API Key", "critical", "CWE-798"),

    # Terraform / Vault
    (r'(?:atlas|terraform)[_-]?token\s*[=:]\s*["\'][^"\']+["\']', "Terraform Token", "critical", "CWE-798"),
    (r'vault[_-]?token\s*[=:]\s*["\'][^"\']+["\']', "Vault Token", "critical", "CWE-798"),

    # Google OAuth / Service Account
    (r'"type"\s*:\s*"service_account"', "GCP Service Account JSON", "critical", "CWE-798"),
    (r'AIza[0-9A-Za-z_-]{35}', "Google API Key", "critical", "CWE-798"),

    # SendGrid / Twilio / Mailgun
    (r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}', "SendGrid API Key", "critical", "CWE-798"),
    (r'\bAC[a-f0-9]{32}\b', "Twilio Account SID", "high", "CWE-798"),
    (r'key-[A-Za-z0-9]{32}', "Mailgun API Key", "critical", "CWE-798"),

    # Generic secret assignment (catch-all, lower confidence)
    (r'(?:secret|private[_-]?key|auth[_-]?token|access[_-]?token)\s*[=:]\s*["\'][^"\']{8,}["\']',
     "Generic Secret", "high", "CWE-798"),
]


# --- Dangerous Code Patterns ---
# Format: (regex, name, severity, category, cwe_id)
DANGEROUS_PATTERNS = [
    # Code Injection
    (r'eval\s*\(', "eval() usage", "critical", "Code Injection", "CWE-95"),
    (r'exec\s*\(', "exec() usage", "critical", "Code Injection", "CWE-95"),
    (r'new\s+Function\s*\(', "Function constructor", "high", "Code Injection", "CWE-95"),
    (r'child_process\.exec\s*\(', "child_process.exec", "high", "Command Injection", "CWE-78"),
    (r'child_process\.execSync\s*\(', "child_process.execSync", "high", "Command Injection", "CWE-78"),
    (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "subprocess.call shell=True", "high", "Command Injection", "CWE-78"),
    (r'subprocess\.Popen\s*\([^)]*shell\s*=\s*True', "subprocess.Popen shell=True", "high", "Command Injection", "CWE-78"),
    (r'subprocess\.run\s*\([^)]*shell\s*=\s*True', "subprocess.run shell=True", "high", "Command Injection", "CWE-78"),
    (r'os\.system\s*\(', "os.system()", "high", "Command Injection", "CWE-78"),
    (r'os\.popen\s*\(', "os.popen()", "high", "Command Injection", "CWE-78"),

    # XSS
    (r'dangerouslySetInnerHTML', "dangerouslySetInnerHTML", "high", "XSS", "CWE-79"),
    (r'\.innerHTML\s*=', "innerHTML assignment", "medium", "XSS", "CWE-79"),
    (r'document\.write\s*\(', "document.write", "medium", "XSS", "CWE-79"),
    (r'v-html\s*=', "Vue v-html directive", "medium", "XSS", "CWE-79"),
    (r'\[innerHTML\]\s*=', "Angular innerHTML binding", "medium", "XSS", "CWE-79"),

    # SQL Injection
    (r'["\'][^"\']*\+\s*[a-zA-Z_]+\s*\+\s*["\'].*(?:SELECT|INSERT|UPDATE|DELETE)',
     "SQL String Concat", "critical", "SQL Injection", "CWE-89"),
    (r'f"[^"]*(?:SELECT|INSERT|UPDATE|DELETE)[^"]*\{',
     "SQL f-string", "critical", "SQL Injection", "CWE-89"),
    (r'f\'[^\']*(?:SELECT|INSERT|UPDATE|DELETE)[^\']*\{',
     "SQL f-string (single quote)", "critical", "SQL Injection", "CWE-89"),
    (r'\.raw\s*\(\s*[`"\'].*\$\{', "Raw SQL with template literal", "critical", "SQL Injection", "CWE-89"),
    (r'\.query\s*\(\s*[`"\'].*\+', "SQL query with concat", "high", "SQL Injection", "CWE-89"),
    (r'(?:execute|query)\s*\(\s*["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*["\']\s*%\s*(?:\(|[a-zA-Z_])',
     "SQL % formatting", "critical", "SQL Injection", "CWE-89"),

    # Template Injection (SSTI)
    (r'render_template_string\s*\(', "render_template_string (SSTI)", "critical", "Template Injection", "CWE-1336"),
    (r'Jinja2.*\bfrom_string\b', "Jinja2 from_string", "high", "Template Injection", "CWE-1336"),
    (r'template\.render\s*\(.*\brequest\b', "Template render with request data", "medium", "Template Injection", "CWE-1336"),

    # Path Traversal
    (r'fs\.readFile(?:Sync)?\s*\([^)]*(?:req\.|params|query|body)',
     "fs.readFile with user input", "critical", "Path Traversal", "CWE-22"),
    (r'(?<!os\.p)open\s*\([^)]*(?:request|params|input)',
     "open() with user input", "high", "Path Traversal", "CWE-22"),
    (r'\.\./', "Path traversal pattern", "medium", "Path Traversal", "CWE-22"),

    # SSRF
    (r'(?:fetch|axios|requests\.(?:get|post|put|delete)|urllib\.request\.urlopen|http\.get)\s*\([^)]*(?:req(?:uest)?[\.\[]|params|query|body|user)',
     "HTTP request with user input (SSRF)", "critical", "SSRF", "CWE-918"),

    # Open Redirect
    (r'(?:redirect|location\.href|window\.location)\s*[=\(]\s*(?:req(?:uest)?[\.\[]|params|query|body|user)',
     "Open Redirect", "high", "Open Redirect", "CWE-601"),

    # Prototype Pollution
    (r'Object\.assign\s*\(\s*\{\}.*(?:req(?:uest)?[\.\[]|params|body|input)',
     "Object.assign with user input", "high", "Prototype Pollution", "CWE-1321"),
    (r'(?:lodash|_)\.merge\s*\(', "lodash.merge (prototype pollution risk)", "medium", "Prototype Pollution", "CWE-1321"),
    (r'(?:lodash|_)\.defaultsDeep\s*\(', "lodash.defaultsDeep (prototype pollution)", "medium", "Prototype Pollution", "CWE-1321"),

    # Insecure configurations
    (r'verify\s*=\s*False', "SSL Verify Disabled", "high", "MITM", "CWE-295"),
    (r'--insecure', "Insecure flag", "medium", "MITM", "CWE-295"),
    (r'disable[_-]?ssl', "SSL Disabled", "high", "MITM", "CWE-295"),
    (r'rejectUnauthorized\s*:\s*false', "TLS rejectUnauthorized disabled", "high", "MITM", "CWE-295"),
    (r'NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*["\']?0', "Node TLS check disabled", "critical", "MITM", "CWE-295"),

    # Unsafe deserialization
    (r'pickle\.loads?\s*\(', "pickle usage", "high", "Deserialization", "CWE-502"),
    (r'yaml\.load\s*\([^)]*\)(?!\s*,\s*Loader)', "Unsafe YAML load", "high", "Deserialization", "CWE-502"),
    (r'marshal\.loads?\s*\(', "marshal usage", "high", "Deserialization", "CWE-502"),
    (r'shelve\.open\s*\(', "shelve (pickle-based)", "medium", "Deserialization", "CWE-502"),
    (r'jsonpickle\.decode\s*\(', "jsonpickle decode", "high", "Deserialization", "CWE-502"),

    # Log Injection
    (r'(?:logger|logging|console\.log)\s*[\.(]\s*.*(?:req\.|params|query|body|user)',
     "Logging user input (log injection)", "medium", "Log Injection", "CWE-117"),

    # Weak Crypto
    (r'(?:md5|sha1)\s*\(', "Weak hash function (MD5/SHA1)", "medium", "Weak Crypto", "CWE-328"),
    (r'\b(?:3DES|DES-CBC|DES-ECB|RC4|RC2|Blowfish)\b', "Weak cipher algorithm", "medium", "Weak Crypto", "CWE-327"),
    (r'Math\.random\s*\(', "Math.random for security", "medium", "Weak Randomness", "CWE-338"),

    # --- Solidity / Smart Contract Patterns ---
    # Reentrancy: external call before state update (SWC-107, ~$300M+ historical losses)
    (r'\.call\{value:', "External call with value (reentrancy risk)", "critical", "Reentrancy", "CWE-841"),
    (r'\.call\.value\s*\(', "External call.value (legacy, reentrancy)", "critical", "Reentrancy", "CWE-841"),
    (r'\.send\s*\(', "send() for ETH transfer (reentrancy risk)", "high", "Reentrancy", "CWE-841"),
    (r'\.transfer\s*\(', "transfer() for ETH (2300 gas limit)", "medium", "Reentrancy", "CWE-841"),

    # Arbitrary Execution: delegatecall / selfdestruct (SwapNet $13.4M, SWC-112)
    (r'\.delegatecall\s*\(', "delegatecall (arbitrary code execution)", "critical", "Arbitrary Call", "CWE-829"),
    (r'\bselfdestruct\s*\(', "selfdestruct (EIP-6780 restricted post-Dencun)", "critical", "Deprecated Opcode", "CWE-665"),
    (r'\bsuicide\s*\(', "suicide() — deprecated selfdestruct alias", "critical", "Deprecated Opcode", "CWE-665"),

    # Access Control (SWC-105, SWC-115)
    (r'\btx\.origin\b', "tx.origin for auth (phishing risk, SWC-115)", "high", "Access Control", "CWE-284"),
    (r'function\s+\w+\s*\([^)]*\)\s*(?:external|public)\s*\{?\s*$',
     "Public/external function without modifier", "medium", "Access Control", "CWE-284"),

    # Oracle Manipulation (YieldBlox $10.2M)
    (r'getReserves\s*\(\s*\)', "AMM getReserves (spot price, flash-loan vulnerable)", "high", "Oracle Manipulation", "CWE-345"),
    (r'latestRoundData\s*\(\s*\)', "Chainlink latestRoundData (check staleness)", "medium", "Oracle Manipulation", "CWE-345"),

    # Unchecked Return Values (SWC-104)
    (r'\.call\s*\(', "Low-level call (check return value)", "high", "Unchecked Return", "CWE-252"),

    # Unprotected Initializer (re-initialization attack, SWC-118)
    (r'function\s+initialize\s*\(', "Initializer function (verify protection)", "high", "Initialization", "CWE-665"),

    # Integer Overflow/Underflow (pre-0.8.0, SWC-101)
    (r'pragma\s+solidity\s+[\^~]?0\.[0-7]\.', "Solidity <0.8.0 (no overflow protection)", "high", "Integer Overflow", "CWE-190"),

    # Unprotected ETH receive
    (r'receive\s*\(\s*\)\s*external\s+payable\s*\{?\s*\}',
     "Empty receive() — ETH locked forever", "high", "Locked Ether", "CWE-664"),

    # Assembly usage
    (r'\bassembly\s*\{', "Inline assembly (manual audit required)", "medium", "Assembly", "CWE-676"),
]


# --- IaC / Container Patterns ---
# Format: (regex, name, severity, category, cwe_id)
IAC_PATTERNS = [
    # Docker
    (r'FROM\s+.*:latest\b', "Docker image using :latest tag", "medium", "Docker", "CWE-1104"),
    (r'USER\s+root', "Docker running as root", "high", "Docker", "CWE-250"),
    (r'--privileged', "Docker privileged mode", "critical", "Docker", "CWE-250"),
    (r'EXPOSE\s+22\b', "Docker exposing SSH port", "medium", "Docker", "CWE-16"),
    (r'(?:ENV|ARG)\s+.*(?:PASSWORD|SECRET|TOKEN|KEY)\s*=\s*\S+',
     "Secret in Dockerfile ENV/ARG", "critical", "Docker", "CWE-798"),
    (r'curl\s+.*\|\s*(?:bash|sh)', "Pipe curl to shell in Dockerfile", "high", "Docker", "CWE-829"),
    (r'--no-check-certificate', "wget without certificate check", "high", "Docker", "CWE-295"),

    # Kubernetes
    (r'privileged\s*:\s*true', "K8s privileged container", "critical", "Kubernetes", "CWE-250"),
    (r'runAsUser\s*:\s*0\b', "K8s running as root (UID 0)", "high", "Kubernetes", "CWE-250"),
    (r'hostNetwork\s*:\s*true', "K8s host network enabled", "high", "Kubernetes", "CWE-16"),
    (r'hostPID\s*:\s*true', "K8s host PID namespace", "high", "Kubernetes", "CWE-16"),
    (r'hostPath\s*:', "K8s hostPath volume mount", "medium", "Kubernetes", "CWE-16"),
    (r'allowPrivilegeEscalation\s*:\s*true', "K8s privilege escalation allowed", "high", "Kubernetes", "CWE-250"),
    (r'readOnlyRootFilesystem\s*:\s*false', "K8s writable root filesystem", "medium", "Kubernetes", "CWE-732"),
    (r'capabilities\s*:\s*\n\s*add\s*:\s*\n\s*-\s*(?:ALL|SYS_ADMIN)',
     "K8s dangerous capabilities", "critical", "Kubernetes", "CWE-250"),

    # Terraform
    (r'cidr_blocks\s*=\s*\[\s*"0\.0\.0\.0/0"\s*\]',
     "Terraform open CIDR (0.0.0.0/0)", "high", "Terraform", "CWE-284"),
    (r'acl\s*=\s*"public-read"', "Terraform public S3 bucket", "critical", "Terraform", "CWE-732"),
    (r'acl\s*=\s*"public-read-write"', "Terraform public-read-write S3", "critical", "Terraform", "CWE-732"),
    (r'encrypted\s*=\s*false', "Terraform encryption disabled", "high", "Terraform", "CWE-311"),
    (r'publicly_accessible\s*=\s*true', "Terraform public database", "critical", "Terraform", "CWE-284"),
    (r'enable_logging\s*=\s*false', "Terraform logging disabled", "medium", "Terraform", "CWE-778"),
    (r'ingress\s*\{[^}]*from_port\s*=\s*0\s*.*to_port\s*=\s*65535',
     "Terraform all-ports ingress rule", "critical", "Terraform", "CWE-284"),

    # CloudFormation
    (r'PubliclyAccessible\s*:\s*true', "CloudFormation public resource", "critical", "CloudFormation", "CWE-284"),

    # General IaC
    (r'disable_password_authentication\s*=\s*false', "Password auth enabled (IaC)", "high", "IaC", "CWE-287"),
    (r'enable_https_traffic_only\s*=\s*false', "HTTPS not enforced (IaC)", "high", "IaC", "CWE-319"),
]


# --- Configuration Issue Patterns ---
# Format: (regex, name, severity, cwe_id)
CONFIG_PATTERNS = [
    (r'"DEBUG"\s*:\s*true', "Debug mode enabled", "high", "CWE-489"),
    (r'debug\s*=\s*True', "Debug mode enabled", "high", "CWE-489"),
    (r'"CORS_ALLOW_ALL".*true', "CORS allow all", "high", "CWE-942"),
    (r'"Access-Control-Allow-Origin".*\*', "CORS wildcard", "high", "CWE-942"),
    (r'X-Frame-Options.*ALLOWALL', "Clickjacking protection disabled", "medium", "CWE-1021"),
    (r'Content-Security-Policy.*unsafe-inline', "CSP unsafe-inline", "medium", "CWE-79"),
]
