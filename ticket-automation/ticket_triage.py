#!/usr/bin/env python3
"""
ticket_triage.py

A small help-desk automation tool.

Reads a CSV of support tickets, automatically assigns each one a CATEGORY and a
PRIORITY based on keywords in the subject and description, then prints a triage
summary. The idea is to take the repetitive "read it and sort it" step off the
technician's plate so they can start with the most urgent work.

Usage:
    python ticket_triage.py sample_tickets.csv

Input CSV columns: id, subject, description
Uses only the Python standard library, so it runs anywhere with no installs.
"""

import csv
import sys
from collections import Counter

# --- Rules -------------------------------------------------------------------
# Each category maps to keywords we look for. First match wins, top to bottom,
# so more specific categories should come before general ones.
CATEGORY_KEYWORDS = {
    "Account/Access": ["password", "locked", "login", "lockout", "reset", "account"],
    "Network/VPN":    ["vpn", "dns", "wifi", "wi-fi", "internet", "connect", "network"],
    "Email":          ["email", "outlook", "mailbox", "smtp"],
    "Printing":       ["printer", "print", "spooler", "toner"],
    "Hardware":       ["monitor", "laptop", "keyboard", "mouse", "slow", "boot", "freeze"],
    "Software":       ["install", "software", "application", "license", "update"],
}

# Words that signal a high-impact, urgent issue.
HIGH_PRIORITY_KEYWORDS = ["down", "outage", "unreachable", "whole team", "everyone",
                          "no one", "server", "critical", "urgent"]
# Words that usually mean a routine, non-urgent request.
LOW_PRIORITY_KEYWORDS = ["request", "new", "would like", "please install", "nice to have"]

# Sort order for displaying priorities most-urgent first.
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def categorize(text):
    """Return the first category whose keyword appears in the text."""
    text = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return category
    return "Uncategorized"


def prioritize(text):
    """Return High / Medium / Low based on keywords."""
    text = text.lower()
    if any(word in text for word in HIGH_PRIORITY_KEYWORDS):
        return "High"
    if any(word in text for word in LOW_PRIORITY_KEYWORDS):
        return "Low"
    return "Medium"


def load_tickets(path):
    """Read tickets from a CSV file into a list of dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def triage(tickets):
    """Add category and priority to each ticket."""
    for t in tickets:
        text = f"{t.get('subject', '')} {t.get('description', '')}"
        t["category"] = categorize(text)
        t["priority"] = prioritize(text)
    return tickets


def print_report(tickets):
    """Print a readable triage summary, most urgent first."""
    tickets.sort(key=lambda t: PRIORITY_ORDER.get(t["priority"], 99))

    print("\n" + "=" * 60)
    print(f"TICKET TRIAGE SUMMARY  ({len(tickets)} tickets)")
    print("=" * 60)

    for t in tickets:
        print(f"[{t['priority']:<6}] #{t['id']}  ({t['category']})")
        print(f"          {t['subject']}")

    # Quick counts so a lead can see the shape of the queue at a glance.
    print("\n" + "-" * 60)
    print("By priority:", dict(Counter(t["priority"] for t in tickets)))
    print("By category:", dict(Counter(t["category"] for t in tickets)))
    print("-" * 60 + "\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: python ticket_triage.py <tickets.csv>")
        sys.exit(1)

    try:
        tickets = load_tickets(sys.argv[1])
    except FileNotFoundError:
        print(f"Error: file not found -> {sys.argv[1]}")
        sys.exit(1)

    if not tickets:
        print("No tickets found in the file.")
        sys.exit(0)

    print_report(triage(tickets))


if __name__ == "__main__":
    main()
