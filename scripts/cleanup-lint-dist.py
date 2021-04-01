"""Tiny script to easily clean-up the lint-dist directory."""
import os

lint_dir = "./lint-dist"
for filename in os.listdir(lint_dir):
    os.remove(os.path.join(lint_dir, filename))

os.rmdir(lint_dir)
