"""Streamlit entrypoint compatibility wrapper."""

from clinical_coder.ui.app import main

__all__ = ["main"]


if __name__ == "__main__":
    main()
