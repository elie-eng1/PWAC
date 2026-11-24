
from dnslib import DNSRecord
from dnslib.server import DNSServer, BaseResolver
import json
import time
import threading

from urllib.request import urlopen
from urllib.error import URLError

API_URL = "http://127.0.0.1:8000/rules"
UPSTREAM_DNS = "1.1.1.1"


class PWACResolver(BaseResolver):

    def __init__(self):
        self.blocked_domains = set()
        self.lock = threading.Lock()

    def update_rules(self):
        try:
            with urlopen(API_URL, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))

            new_rules = {
                rule[1].lower().strip(".")
                for rule in data["website_rules"]
                if rule[2]
            }

            with self.lock:
                self.blocked_domains = new_rules

            print("DNS rules synchronized.")
            print("Blocked domains:", len(new_rules))

        except (URLError, ValueError, KeyError) as error:
            print("Could not update DNS rules:", error)

    def is_blocked(self, domain):
        domain = domain.lower().strip(".")

        with self.lock:
            blocked = set(self.blocked_domains)

        return any(
            domain == item or domain.endswith("." + item)
            for item in blocked
        )

    def resolve(self, request, handler):
        domain = str(request.q.qname).lower().strip(".")

        if self.is_blocked(domain):
            print("BLOCKED:", domain)

            reply = request.reply()
            reply.header.rcode = 3
            return reply

        print("FORWARDING:", domain)

        try:
            response = request.send(
                UPSTREAM_DNS,
                53,
                timeout=5
            )

            return DNSRecord.parse(response)

        except Exception as error:
            print("DNS forwarding error:", error)

            reply = request.reply()
            reply.header.rcode = 2
            return reply



if __name__ == "__main__":

    resolver = PWACResolver()

    print("Starting PWAC DNS Filter...")

    # Synchronize rules before starting
    resolver.update_rules()

    udp_server = DNSServer(
        resolver,
        port=5353,
        address="127.0.0.1",
        tcp=False
    )

    tcp_server = DNSServer(
        resolver,
        port=5353,
        address="127.0.0.1",
        tcp=True
    )

    try:
        udp_server.start_thread()
        tcp_server.start_thread()

        print("\nPWAC DNS Filter started.")
        print("UDP and TCP enabled.")
        print("Listening on 127.0.0.1:5353")
        print("Rules synchronize every 10 seconds.")
        print("Press CTRL + C to stop.")

        while True:
            time.sleep(10)
            resolver.update_rules()

    except KeyboardInterrupt:
        print("\nStopping PWAC DNS Filter...")

    finally:
        udp_server.stop()
        tcp_server.stop()
        print("PWAC DNS Filter stopped.")
