import random
import re
import time
from urllib.parse import quote

from playwright.sync_api import sync_playwright, TimeoutError

import config


def load_contacts():
    contacts = []

    with open(config.CONTACTS_FILE, encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if line:
                contacts.append(line)

    return contacts


def normalize(phone: str):
    """
    Accepts:
        13991811779
        (13) 99181-1779
        +55 13 99181-1779
        5513991811779

    Returns:
        5513991811779
    """

    phone = re.sub(r"\D", "", phone)

    # Already E.164
    if phone.startswith("55") and len(phone) in (12, 13):
        return phone

    # Brazilian domestic
    if len(phone) in (10, 11):
        return "55" + phone

    return None


def load_log(path):
    if not path.exists():
        return set()

    return {
        x.strip()
        for x in path.read_text().splitlines()
        if x.strip()
    }


def append_log(path, value):
    with open(path, "a", encoding="utf8") as f:
        f.write(value + "\n")


def random_delay():
    delay = random.uniform(
        config.MIN_DELAY,
        config.MAX_DELAY,
    )

    print(f"Waiting {delay:.1f}s...")
    time.sleep(delay)


def long_break():
    delay = random.randint(
        config.LONG_BREAK_MIN,
        config.LONG_BREAK_MAX,
    )

    print(f"\nLong break ({delay}s)\n")
    time.sleep(delay)


def send(page, phone):

    url = (
        "https://web.whatsapp.com/send"
        f"?phone={phone}"
        f"&text={quote(config.MESSAGE)}"
    )

    page.goto(url)

    # Wait until WhatsApp actually opens the chat.
    page.wait_for_url(
        re.compile(r".*send.*"),
        timeout=30000,
    )

    # Wait for the composer to exist.
    page.wait_for_selector(
        "div[contenteditable='true']",
        timeout=30000,
    )

    # Give WhatsApp another second to finish rendering.
    time.sleep(2)

    # Send the pre-filled message.
    page.keyboard.press("Enter")

    # Tiny pause so the send completes.
    time.sleep(1)


def main():

    config.ERROR_DIR.mkdir(exist_ok=True)

    contacts = load_contacts()

    already_sent = load_log(config.SENT_LOG)

    remaining = []

    for phone in contacts:

        normalized = normalize(phone)

        if normalized is None:
            print(f"Skipping invalid number: {phone}")
            append_log(config.FAILED_LOG, phone)
            continue

        if normalized not in already_sent:
            remaining.append(normalized)

    print(f"Loaded: {len(contacts)}")
    print(f"Already sent: {len(already_sent)}")
    print(f"Remaining: {len(remaining)}")

    if not remaining:
        return

    with sync_playwright() as p:

        browser = p.chromium.launch_persistent_context(
            config.USER_DATA_DIR,
            headless=False,
        )

        page = browser.new_page()

        page.goto("https://web.whatsapp.com")

        input(
            "\nLog into WhatsApp if needed.\n"
            "When your chats are visible press ENTER..."
        )

        break_after = random.randint(
            config.BREAK_EVERY_MIN,
            config.BREAK_EVERY_MAX,
        )

        sent_since_break = 0

        total = len(remaining)

        for index, phone in enumerate(remaining, start=1):

            print(f"\n[{index}/{total}] {phone}")

            success = False

            for attempt in range(2):

                try:

                    send(page, phone)

                    append_log(config.SENT_LOG, phone)

                    print("✓ Sent")

                    success = True
                    sent_since_break += 1

                    break

                except TimeoutError:

                    print("Timed out.")

                except Exception as e:

                    print(e)

                page.screenshot(
                    path=str(
                        config.ERROR_DIR /
                        f"{phone}.png"
                    )
                )

                if attempt == 0:
                    print(
                        f"Retrying in {config.RETRY_DELAY}s..."
                    )
                    time.sleep(config.RETRY_DELAY)

            if not success:

                append_log(config.FAILED_LOG, phone)
                print("✗ Failed")

            random_delay()

            if sent_since_break >= break_after:

                long_break()

                sent_since_break = 0

                break_after = random.randint(
                    config.BREAK_EVERY_MIN,
                    config.BREAK_EVERY_MAX,
                )

        browser.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
