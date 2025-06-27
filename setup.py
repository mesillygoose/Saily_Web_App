import os
import subprocess
import sys

def create_folders():
    """Create necessary folders"""
    folders = ['templates', 'data']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created {folder} folder")
        else:
            print(f"{folder} folder already exists")
def install_flask():
    """Install Flask if not already installed"""
    try:
        import flask
        print(f"Flask is already installed (version {flask.__version__})")
    except ImportError:
        print("Installing Flask...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask"])
            print("Flask installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install Flask. Please run: pip install Flask")
            return False
    return True
def check_files():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'templates/base.html',
        'templates/index.html',
        'templates/purchase.html',
        'templates/destinations.html',
        'templates/my_plans.html',
        'templates/top_up.html'
    ]
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"{file}")
        else:
            print(f"{file} - MISSING!")
            missing_files.append(file)
    return missing_files
def main():
    print("Saily eSIM Management - Setup Script")
    print("=" * 50)
    print("\n1. Creating folders...")
    create_folders()
    print("\n2. Checking Flask installation...")
    if not install_flask():
        return
    print("\n3. Checking required files...")
    missing = check_files()
    if missing:
        print(f"\nMissing {len(missing)} files:")
        for file in missing:
            print(f" - {file}")
        print("\nPlease create these files by copying the code from the artifacts.")
    else:
        print("\nAll files are present!")
        print("\nSetup complete! To run the app:")
        print("1. Run: python app.py")
        print("2. Open browser to: http://localhost:5000")
if __name__ == "__main__":
    main()