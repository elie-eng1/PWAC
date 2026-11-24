
import json
import time
import re

from urllib.request import urlopen
from urllib.error import URLError, HTTPError

API_URL = "http://127.0.0.1:8000/rules"


def get_website_rules():
    try:
        with urlopen(API_URL, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data["website_rules"]

    except (HTTPError, URLError, KeyError, ValueError) as error:
        print("Backend error:", error)
        return None


def preview_rules(rules):
    print("\n========== PWAC PREVIEW ==========")

    blocked_count = 0
    allowed_count = 0

    for rule in rules:
        rule_id, domain, is_blocked, created_at = rule

        domain = domain.lower().strip()

        # Accept only valid domain names.
        if not re.fullmatch(
            r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}",
            domain
        ):
            print(f"INVALID DOMAIN: {domain}")
            continue

        if is_blocked:
            print(f"WOULD BLOCK: {domain}")
            blocked_count += 1
        else:
            print(f"WOULD ALLOW: {domain}")
            allowed_count += 1

    print("----------------------------------")
    print("Blocked:", blocked_count)
    print("Allowed:", allowed_count)
    print("PREVIEW ONLY - Windows not modified.")
    print("==================================")


if __name__ == "__main__":
    print("PWAC Windows Agent started.")
    print("Safe preview mode enabled.")
    print("Checking rules every 10 seconds.")
    print("Press CTRL + C to stop.")

    try:
        while True:
            rules = get_website_rules()

            if rules is not None:
                preview_rules(rules)

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nPWAC agent stopped.")
