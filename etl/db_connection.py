"""Robust database connection handling with retries and keep-alive for Supabase."""
import os
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional


def get_database_url() -> str:
    """Get DATABASE_URL with SSL mode configured for Supabase."""
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Add sslmode=require for Supabase pooler connections
    if 'sslmode' not in db_url:
        db_url += '?sslmode=require' if '?' not in db_url else '&sslmode=require'
    
    return db_url


def connect_with_retry(max_attempts: int = 5, autocommit: bool = False):
    """
    Connect to PostgreSQL with automatic retry logic and keep-alive settings.
    
    This ensures connections work even after idle periods (important for 6 AM automated loads).
    
    Args:
        max_attempts: Maximum connection attempts (default 5)
        autocommit: Enable autocommit mode (default False)
    
    Returns:
        psycopg2 connection object
    
    Raises:
        psycopg2.OperationalError: If all retry attempts fail
    """
    db_url = get_database_url()
    
    for attempt in range(1, max_attempts + 1):
        try:
            # Connect with keep-alive settings for long-running connections
            conn = psycopg2.connect(
                db_url,
                connect_timeout=10,      # 10 second connection timeout
                keepalives=1,            # Enable TCP keepalives
                keepalives_idle=30,      # Start keepalives after 30 seconds idle
                keepalives_interval=10,  # Send keepalive every 10 seconds
                keepalives_count=5       # Close connection after 5 failed keepalives
            )
            
            if autocommit:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            # Test the connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            
            if attempt > 1:
                print(f"✓ Database connection established on attempt {attempt}")
            
            return conn
            
        except psycopg2.OperationalError as e:
            print(f"⚠️ Connection attempt {attempt}/{max_attempts} failed: {str(e)[:100]}")
            
            if attempt < max_attempts:
                # Exponential backoff: 2, 4, 8, 16 seconds
                wait_time = 2 ** attempt
                print(f"   Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ All {max_attempts} connection attempts failed")
                raise
    
    raise psycopg2.OperationalError("Failed to connect after all retry attempts")


def execute_with_retry(query: str, params: Optional[tuple] = None, fetch_one: bool = False, fetch_all: bool = False):
    """
    Execute a query with automatic connection retry.
    
    Args:
        query: SQL query to execute
        params: Query parameters
        fetch_one: Return single row result
        fetch_all: Return all row results
    
    Returns:
        Query result or None
    """
    conn = None
    try:
        conn = connect_with_retry(autocommit=True)
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            return cursor.rowcount
            
    finally:
        if conn:
            conn.close()
