#!/bin/bash
# Publish to PyPI

echo "Building package..."
python -m build

echo "Uploading to PyPI..."
python -m twine upload dist/*

echo "Done! metanoia-qa v2.1.0 published to PyPI"
