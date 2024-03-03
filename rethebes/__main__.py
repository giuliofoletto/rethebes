"""
Allow rethebes to be executable through `python -m rethebes`.

Authors: Giulio Foletto.
License: See project-level license file.
"""


# Encapsulation in condition is necessary because otherwise subprocess might re-execute this module.
# This would not be a big deal in this case, because currently only imports are present in cli.
def main():
    from rethebes.cli import cli

    cli()


if __name__ == "__main__":
    main()
