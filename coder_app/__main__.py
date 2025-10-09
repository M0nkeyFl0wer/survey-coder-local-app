"""
Entry point for running coder_app as a module.
Allows execution via: python -m coder_app
"""

from .cli.main import cli

if __name__ == '__main__':
    cli()