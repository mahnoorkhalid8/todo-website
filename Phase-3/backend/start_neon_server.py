#!/usr/bin/env python3
"""Start the backend server with Neon database configuration in a fresh Python process."""

import os
import subprocess
import sys

def main():
    # Set environment variables
    env = os.environ.copy()
    env['DATABASE_URL'] = 'postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'
    env['SECRET_KEY'] = 'o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N'

    # Run the server in a new subprocess with the environment variables set
    cmd = [
        sys.executable,
        "-c",
        """
import uvicorn
from main import app

print('Starting server with Neon database configuration...')
uvicorn.run(
    app,
    host='0.0.0.0',
    port=8000,
    reload=False,
    log_level='info'
)
        """
    ]

    # Execute the command with the updated environment
    subprocess.run(cmd, env=env, cwd=os.path.dirname(__file__))

if __name__ == "__main__":
    main()