
from dnslib import DNSRecord
import sys

DNS_SERVER = "127.0.0.1"
DNS_PORT = 5353

def check_dns(domain):
    try:
        query = DNSRecord.question(domain)

        response = query.send(
            DNS_SERVER,
            port=DNS_PORT,
            timeout=3
        )

        reply = DNSRecord.parse(response)

        if reply.header.rcode == 0:
            return "DNS WORKING"

        if reply.header.rcode == 3:
            return "DOMAIN BLOCKED"

        return f"DNS ERROR: {reply.header.rcode}"

    except Exception as error:
        return f"DNS SERVER UNAVAILABLE: {error}"


if __name__ == "__main__":
    print("========== PWAC HEALTH CHECK ==========")

    for domain in ["google.com", "facebook.com"]:
        print(domain, "|", check_dns(domain))

    print("=======================================")
