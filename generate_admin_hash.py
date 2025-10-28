#!/usr/bin/env python3
"""Generate password hash for admin user"""
from werkzeug.security import generate_password_hash
import getpass

def main():
    print("=" * 60)
    print("ML Competition Platform - Admin Password Hash Generator")
    print("=" * 60)
    print()
    
    password = getpass.getpass("Enter admin password: ")
    confirm = getpass.getpass("Confirm admin password: ")
    
    if password != confirm:
        print("❌ Passwords do not match!")
        return
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters!")
        return
    
    # Generate hash
    hash_value = generate_password_hash(password)
    
    print()
    print("✅ Password hash generated successfully!")
    print()
    print("Copy this hash and use it in Supabase:")
    print("-" * 60)
    print(hash_value)
    print("-" * 60)
    print()
    print("SQL command to update admin user:")
    print(f"UPDATE admin SET password_hash = '{hash_value}' WHERE username = 'isaaceinst3in';")
    print()

if __name__ == "__main__":
    main()
