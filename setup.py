#!/usr/bin/env python3
"""
Setup script for MovieMind application.
Helps users install dependencies and configure the application.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """Print application banner."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎬 MovieMind Setup                        ║
    ║              AI-Powered Movie Recommendations                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def create_virtual_environment():
    """Create a virtual environment."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists.")
        return True
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment.")
        return False


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    # Determine the pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        return False


def create_data_files():
    """Create necessary data files if they don't exist."""
    print("📁 Creating data files...")
    
    data_files = [
        "users.csv",
        "user_activity.csv", 
        "user_reviews.csv"
    ]
    
    for file in data_files:
        if not os.path.exists(file):
            try:
                with open(file, 'w', newline='', encoding='utf-8') as f:
                    if file == "users.csv":
                        f.write("id,username,password,email,created_at\n")
                        f.write("1,demo,demo123,demo@example.com,2024-01-01\n")
                        f.write("2,admin,admin123,admin@example.com,2024-01-01\n")
                    elif file == "user_activity.csv":
                        f.write("user_id,action,title,movie_id,rating,timestamp\n")
                    elif file == "user_reviews.csv":
                        f.write("user,movie_id,title,rating,review\n")
                print(f"✅ Created {file}")
            except Exception as e:
                print(f"❌ Failed to create {file}: {e}")
        else:
            print(f"✅ {file} already exists")


def setup_environment_variables():
    """Guide user through setting up environment variables."""
    print("\n🔧 Environment Variables Setup")
    print("=" * 50)
    
    api_key = input("Enter your TMDB API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Create .env file
        with open(".env", "w") as f:
            f.write(f"TMDB_API_KEY={api_key}\n")
        print("✅ API key saved to .env file")
    else:
        print("ℹ️  No API key provided. App will run in demo mode.")
        print("   Get a free API key from: https://www.themoviedb.org/settings/api")


def show_next_steps():
    """Show next steps for the user."""
    print("\n🚀 Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("2. Run the application:")
    print("   streamlit run app.py")
    
    print("3. Open your browser and go to:")
    print("   http://localhost:8501")
    
    print("\n📝 Demo Credentials:")
    print("   Username: demo, Password: demo123")
    print("   Username: admin, Password: admin123")
    
    print("\n📚 For more information, see README.md")


def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create data files
    create_data_files()
    
    # Setup environment variables
    setup_environment_variables()
    
    # Show next steps
    show_next_steps()


if __name__ == "__main__":
    main()
