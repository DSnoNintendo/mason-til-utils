import smtplib
import dns.resolver
import re

import smtplib, dns.resolver, re

def is_valid_email(email):
    # Format check
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False, "Invalid email format"
    
    domain = email.split("@")[1]
    
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_servers = sorted([(r.preference, str(r.exchange)) for r in mx_records])
        
        # Skip SMTP for Microsoft/Google
        if any("outlook.com" in server or "google.com" in server for _, server in mx_servers):
            return True, "Valid domain (mailbox not verifiable via SMTP)"
        
        # Try SMTP for other domains
        for _, server in mx_servers:
            try:
                with smtplib.SMTP(server, 25, timeout=10) as smtp:
                    smtp.ehlo()
                    smtp.putcmd("MAIL", f"FROM:<verify@example.com>")
                    code, _ = smtp.getreply()
                    if code != 250:
                        continue
                    
                    code, msg = smtp.docmd("RCPT", f"TO:<{email}>")
                    if 200 <= code <= 299:
                        return True, "Valid email address"
                    else:
                        return False, f"Invalid mailbox: {msg.decode()}"
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError):
                continue
                
        return False, "All MX servers failed"
        
    except dns.resolver.NoAnswer:
        return False, "No MX records found"
    except Exception as e:
        return False, f"DNS error: {str(e)}"

if __name__ == "__main__":
    email = input("Enter email address to verify: ")
    is_valid, message = is_valid_email(email)
    print(f"{email}: {message}")