"""
Allow rethebes to be executable through `python -m rethebes`.

Authors: Giulio Foletto.
"""

# Encapsulation in condition is necessary because otherwise subprocess might re-execute this module.
if __name__ == "__main__":
    from rethebes.cli import cli
    cli()