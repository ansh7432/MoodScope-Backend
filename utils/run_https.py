"""
HTTPS Streamlit runner for MoodScope
Enables HTTPS for Spotify OAuth integration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_https_streamlit():
    """Run Streamlit with HTTPS support"""
    
    # Create SSL certificates directory
    ssl_dir = Path("ssl")
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    # Generate self-signed certificate if it doesn't exist
    if not cert_file.exists() or not key_file.exists():
        print("🔐 Generating SSL certificate...")
        
        # Generate self-signed certificate
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", str(key_file),
            "-out", str(cert_file),
            "-days", "365", "-nodes",
            "-subj", "/C=US/ST=State/L=City/O=MoodScope/OU=Dev/CN=127.0.0.1"
        ], check=True)
        
        print("✅ SSL certificate generated")
    
    # Run Streamlit with HTTPS
    print("🚀 Starting MoodScope with HTTPS...")
    print("📱 Access at: https://127.0.0.1:8501")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "enhanced_app.py",
        "--server.port", "8501",
        "--server.sslCertFile", str(cert_file),
        "--server.sslKeyFile", str(key_file),
        "--server.enableCORS", "false"
    ])

if __name__ == "__main__":
    run_https_streamlit()
