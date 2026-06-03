import subprocess
import sys

# ============================================================
# REQUIRED PACKAGES
# ============================================================

PACKAGES = [

    "anthropic",

    "json-repair",

    "graphviz",

    "N2G",

    "pydot",
]

# ============================================================
# INSTALL FUNCTION
# ============================================================

def install(package: str):

    print(f"\nInstalling: {package}")

    subprocess.check_call([

        sys.executable,

        "-m",

        "pip",

        "install",

        package
    ])

    print(f"[OK] Installed: {package}")


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n── Installing Railway OT Dependencies ──"
    )

    for package in PACKAGES:

        try:

            install(package)

        except Exception as e:

            print(
                f"[ERROR] Failed: {package}"
            )

            print(e)

    print(
        "\nDependency installation complete."
    )


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()