"""Compatibility wrapper for the packaged Channel 2 CLI."""

from channel2.main import main


if __name__ == "__main__":
    raise SystemExit(main())