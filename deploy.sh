#!/bin/bash

# Step 1: Make changes to your code
# This step is manual and not included in this script

# Step 2: Update the version number in setup.py and pyproject.toml
# This step is manual and not included in this script
# remember to update the pyproject.toml file as well

# Step 3: Rebuild your package
# Remember to delete the old distribution files in the dist/ directory before running the python setup.py sdist bdist_wheel command to avoid uploading old packages to PyPI
rm -r dist/*
python setup.py sdist bdist_wheel

pyinstaller --noconfirm sesaCanvas.spec
# Step 4: Commit your changes to your local Git repository
git add .
git commit -m "Update package to version 0.1.11" # Replace "x.y.z" with your new version number

# Step 5: Push your changes to GitHub
git push origin main # Replace "main" with the name of your branch if it's different


# git filter-branch --force --index-filter \
#   "git rm --cached --ignore-unmatch build/sesaCanvas/sesaCanvas.pkg" \
#   --prune-empty --tag-name-filter cat -- --all

