"""
main.py
CLI entry point for the infrastructure topology generator.

Usage:
  python main.py
  python main.py --input examples/substation.txt
  python main.py --input examples/substation.txt --output topology.json
"""

import argparse
import json
import os
import sys

import anthropic

from json_repair import repair_json
from prompts import SYSTEM_PROMPT, build_user_prompt
from validator import validate, print_report


def call_llm(description: str) -> dict:
    """Send description to Claude and return repaired topology JSON."""

    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"]
    )

    print("  Generating topology...", flush=True)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8000,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(description)
            }
        ],
    )

    raw = message.content[0].text.strip()


    # Remove markdown fences safely
    if raw.startswith(""):
        raw = raw.replace("json", "")
        raw = raw.replace("```", "")
        raw = raw.strip()

    # Save raw output
    with open(
        "debug_raw_output.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(raw)

    # Attempt direct parse first
    try:
        return json.loads(raw)

    except json.JSONDecodeError:

        print("\n[WARN] Invalid JSON detected.")
        print("Attempting automatic repair...")

        try:

            repaired = repair_json(raw)

            with open(
                "debug_repaired_output.json",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(repaired)

            topology = json.loads(repaired)

            print("[OK] JSON successfully repaired.")

            return topology

        except Exception as e:

            print("\n[ERROR] JSON repair failed:")
            print(e)

            print("\nRaw output saved:")
            print("debug_raw_output.txt")

            sys.exit(1)


def get_description(input_file: str | None) -> str:
    """Read description from file or prompt interactively."""
    if input_file:
        with open(input_file) as f:
            return f.read()

    print("\nDescribe your network infrastructure.")
    print("(Press Enter twice when done)\n")

    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a structured IEC 62443 network topology from a plain-English description."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to a .txt file containing the network description",
        default=None,
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write the topology JSON (default: print to stdout)",
        default=None,
    )
    parser.add_argument(
        "--no-validate",
        help="Skip IEC 62443 compliance validation",
        action="store_true",
    )
    args = parser.parse_args()

    if "ANTHROPIC_API_KEY" not in os.environ:
        print("[ERROR] ANTHROPIC_API_KEY environment variable not set.")
        print("  export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    print("\n── Infra Topology Generator ─────────────────────────────────────")

    description = get_description(args.input)

    if not description:
        print("[ERROR] No description provided.")
        sys.exit(1)

    topology = call_llm(description)

    if not args.no_validate:
        findings = validate(topology)
        print_report(findings)

    output_json = json.dumps(topology, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"  Topology saved to {args.output}")
    else:
        print("── Generated Topology ───────────────────────────────────────────")
        print(output_json)

    print("─────────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()