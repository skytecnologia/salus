import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

"""
Setup database tables

Usage:
    Use default .env.local
    > python scripts/setup_db.py

    Use a specific config file
    > python scripts/setup_db.py --config .env.dev
    > python scripts/setup_db.py -c .env.prod

    Show help
    > python scripts/setup_db.py --help
"""

BASE_DIR = Path(__file__).parent.parent
CONF_DIR = Path(BASE_DIR) / 'conf'

os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Setup database tables')
parser.add_argument(
    '--config',
    '-c',
    type=str,
    default='.env.local',
    help='Configuration file name (default: .env.local)'
)
args = parser.parse_args()

# Load environment variables from the specified config file
env_path = Path(CONF_DIR) / args.config
if not env_path.exists():
    print(f"❌ Error: Configuration file '{env_path}' not found!")
    sys.exit(1)

print(f"📄 Loading configuration from: {args.config}")
load_dotenv(env_path)


from src.core.database import Base, engine, SessionLocal
from src.models import User, Patient


print("🔹 Creating tables if they don't exist...")
engine.echo = True
Base.metadata.create_all(engine)
print("✅ Database setup complete!")

from src.auth.pwd import hash_password
pwd = hash_password("sky2026")
user = User(username='demo', name='Paciente Demo', hashed_password=pwd, is_active=True, is_superuser=False, is_password_expired=False)
db = SessionLocal()
db.add(user)
db.commit()
db.close()
