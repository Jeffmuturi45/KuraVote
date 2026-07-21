# reset_db.py
import os
import sys
import time

def reset_database():
    """Reset the entire database and migrations"""
    
    # 1. Delete database file with retry
    db_file = 'db.sqlite3'
    retries = 3
    for i in range(retries):
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"✅ Deleted {db_file}")
                break
        except PermissionError as e:
            print(f"⚠️ Attempt {i+1}: Database is locked - {e}")
            if i < retries - 1:
                print("   Waiting 2 seconds...")
                time.sleep(2)
                # Try to force delete
                try:
                    os.system(f"del /f {db_file}")
                    print(f"✅ Force deleted {db_file}")
                    break
                except:
                    continue
            else:
                print("❌ Cannot delete database file. Please close any programs using it.")
                print("   Make sure:")
                print("   - Django server is stopped (CTRL+C)")
                print("   - No other applications are accessing the database")
                print("   - Then run: del /f db.sqlite3")
                return False
    
    # 2. Delete migration files
    migrations_dir = 'election/migrations'
    if os.path.exists(migrations_dir):
        for file in os.listdir(migrations_dir):
            if file != '__init__.py' and file.endswith('.py'):
                try:
                    os.remove(os.path.join(migrations_dir, file))
                    print(f"✅ Deleted migration: {file}")
                except PermissionError:
                    print(f"⚠️ Could not delete {file}, skipping...")
        
        # Delete .pyc files
        for file in os.listdir(migrations_dir):
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(migrations_dir, file))
                    print(f"✅ Deleted {file}")
                except PermissionError:
                    pass
    
    print("\n✅ Database reset complete!")
    print("\nNow run these commands:")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")
    print("  python manage.py createsuperuser")
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("DATABASE RESET UTILITY")
    print("="*60)
    print("Make sure the Django server is stopped (CTRL+C)!")
    print("Press ENTER to continue or CTRL+C to cancel...")
    input()
    
    reset_database()