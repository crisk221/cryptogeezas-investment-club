#!/usr/bin/env python3
import os
print("Environment check:")
print(f"PORT environment variable: {os.environ.get('PORT', 'Not set')}")
print(f"Python executable: {os.__file__}")
print("Files in current directory:")
for f in os.listdir("."):
    print(f"  {f}")
