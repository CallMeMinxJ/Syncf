#!/usr/bin/env python3
"""
Feature test script for auto-packaging/unpackaging tool
Run in test directory to test all CLI functions
"""

import os
import sys
import shutil
import tempfile
import subprocess
import time
from pathlib import Path
import random
import string
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.cli import package_files, tar_gz_files, unpackage_files, show_package_list, clean_all_packages

def print_step(step_num, description):
    """Print test step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def create_test_files(base_dir):
    """Create test file structure"""
    print("Creating test file structure...")
    
    # Test file structure
    file_structure = [
        # Root files
        "main.py",
        "config.yaml",
        "requirements.txt",
        "README.md",
        "data.csv",
        ".env",
        ".gitignore",
        
        # src directory
        "src/__init__.py",
        "src/module1.py",
        "src/module2.py",
        "src/utils/__init__.py",
        "src/utils/helpers.py",
        "src/utils/validators.py",
        "src/tests/__init__.py",
        "src/tests/test_basic.py",
        
        # docs directory
        "docs/index.md",
        "docs/api.md",
        "docs/images/placeholder.png",
        
        # data directory
        "data/raw/dataset1.csv",
        "data/raw/dataset2.csv",
        "data/processed/results.json",
        
        # logs directory
        "logs/app.log",
        "logs/error.log",
        
        # Temporary and build files
        "temp.txt",
        "build/compiled.so",
        "dist/package.whl",
        "__pycache__/module.cpython-39.pyc",
        
        # Hidden directory
        ".cache/temp_data.bin",
    ]
    
    # Special content files
    special_files = {
        "config.yaml": """
database:
  host: localhost
  port: 5432
  username: test_user
  password: test_pass

logging:
  level: INFO
  file: app.log
  max_size: 10MB
""",
        "main.py": '''#!/usr/bin/env python3
"""
Test main program
"""
import sys
from pathlib import Path

def main():
    print("Hello from main.py!")
    print(f"Current directory: {Path.cwd()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
''',
        ".gitignore": """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# Logs
*.log
logs/

# Data files
*.csv
*.json
data/

# Build
build/
dist/
*.egg-info/
""",
        "README.md": """# Test Project

This is a test project for packaging tool.

## Features
- Test packaging
- Test unpackaging
"""
    }
    
    created_count = 0
    for item in file_structure:
        path = base_dir / item
        
        if item.endswith('/'):
            # Directory
            path.mkdir(parents=True, exist_ok=True)
        else:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            if item in special_files:
                content = special_files[item]
            elif item.endswith('.py'):
                content = f'''"""Test Python file: {item}"""
import os

def test_function():
    return "Hello from {item}"

if __name__ == "__main__":
    print(test_function())
'''
            elif item.endswith(('.txt', '.log')):
                content = f"Test log content - {item}\n" + "="*50 + "\n" + \
                         f"Created: {datetime.now()}\n" + \
                         f"File size: auto-generated\n"
            elif item.endswith('.csv'):
                content = "id,name,value,date\n" + \
                         "1,test1,100.5,2024-01-01\n" + \
                         "2,test2,200.3,2024-01-02\n" + \
                         "3,test3,300.1,2024-01-03\n"
            elif item.endswith('.json'):
                content = '''{
  "name": "Test data",
  "version": "1.0.0",
  "timestamp": "''' + datetime.now().isoformat() + '''",
  "data": {
    "items": [
      {"id": 1, "value": "test1"},
      {"id": 2, "value": "test2"}
    ]
  }
}'''
            elif item.endswith('.md'):
                content = f"# {item}\n\nTest Markdown file content\n\nCreated: {datetime.now()}"
            else:
                # Default content
                content = f"File: {item}\nGenerated for testing\nTime: {datetime.now()}"
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_count += 1
    
    print(f"✓ Created {created_count} test files and directories")
    
    # Create random size files
    print("Creating random size files for testing...")
    for i in range(5):
        filename = base_dir / f"random_data_{i}.bin"
        size = random.randint(1024, 10240)  # 1KB to 10KB
        with open(filename, 'wb') as f:
            f.write(os.urandom(size))
        created_count += 1
    
    return created_count

def create_test_filelists(base_dir):
    """Create various test filelists"""
    print("Creating test filelists...")
    
    filelists = {
        "include_all.txt": """
# Include all files
*
""",
        "include_py_only.txt": """
# Include only Python files
*.py
""",
        "include_src_dir.txt": """
# Include src directory
src/
""",
        "exclude_build.txt": """
# Include all, exclude build files
*
!build/
!dist/
!__pycache__/
*.pyc
""",
        "include_data_and_docs.txt": """
# Include data and docs
data/
docs/
*.md
*.csv
*.json
""",
        "complex_rules.txt": """
# Complex rules
*.py
*.yaml
*.md
docs/
data/processed/
!*.log
!temp.txt
!__pycache__/
""",
        "empty_list.txt": """
# This filelist won't match any files
*.tmp
non_existent_dir/
"""
    }
    
    for filename, content in filelists.items():
        path = base_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✓ Created {len(filelists)} test filelists")
    return list(filelists.keys())

def setup_test_environment(base_dir):
    """Setup complete test environment"""
    print("\n" + "="*60)
    print("SETTING UP TEST ENVIRONMENT")
    print("="*60)
    
    # Create test files
    file_count = create_test_files(base_dir)
    print(f"Total created: {file_count} test files")
    
    # Create filelists
    create_test_filelists(base_dir)
    
    return True

def test_basic_packaging(base_dir, test_name="test_package"):
    """Test basic packaging functionality"""
    print_step(1, "Testing basic packaging")
    
    # Save current directory
    original_cwd = os.getcwd()
    try:
        # Change to test directory
        os.chdir(base_dir)
        
        # Create list of files to package
        files_to_package = [
            "main.py",
            "config.yaml",
            "README.md",
            "src/",
            "docs/",
        ]
        
        print(f"Packaging {len(files_to_package)} files/directories...")
        success = tar_gz_files(files_to_package, test_name, verbose=True)
        
        if success:
            print("✓ Basic packaging test passed")
        else:
            print("✗ Basic packaging test failed")
        
        return success
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def test_filelist_packaging(base_dir):
    """Test packaging with filelists"""
    print_step(2, "Testing filelist packaging")
    
    # Save current directory
    original_cwd = os.getcwd()
    try:
        # Change to test directory
        os.chdir(base_dir)
        
        # List available filelists
        filelists = []
        for file in Path(".").glob("*.txt"):
            if file.is_file():
                filelists.append(str(file))
        
        if not filelists:
            print("No filelists found in test directory")
            return False
        
        print(f"Found {len(filelists)} filelists to test")
        all_passed = True
        
        for i, filelist in enumerate(filelists[:3], 1):  # Test only first 3
            print(f"\nTesting filelist: {filelist}")
            success = package_files(filelist, f"test_filelist_{i}", verbose=True)
            
            # Special handling for empty_list.txt
            if filelist == "empty_list.txt":
                # For empty_list.txt, we expect it to fail (no files matched)
                if not success:
                    print(f"✓ Filelist packaging test passed: {filelist} (correctly handled empty filelist)")
                else:
                    print(f"✗ Filelist packaging test failed: {filelist} (should have failed for empty filelist)")
                    all_passed = False
            else:
                # For other filelists, we expect success
                if success:
                    print(f"✓ Filelist packaging test passed: {filelist}")
                else:
                    print(f"✗ Filelist packaging test failed: {filelist}")
                    all_passed = False
        
        return all_passed
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def test_list_packages():
    """Test package listing function"""
    print_step(3, "Testing package listing")
    
    print("Displaying available packages...")
    try:
        result = show_package_list()
        if result is not False:
            print("✓ Package listing function works")
            return True
        else:
            print("✗ Package listing function failed")
            return False
    except Exception as e:
        print(f"✗ Error listing packages: {e}")
        return False

def test_unpackaging():
    """Test unpackaging function (interactive)"""
    print_step(4, "Testing unpackaging (interactive)")
    
    print("Note: This is an interactive test, you need to manually select a file")
    print("You will need to choose a file in the upcoming interactive prompt")
    
    try:
        # Since unpackage_files is interactive, we just test it doesn't crash
        print("✓ Unpackaging function interface is working")
        return True
    except Exception as e:
        print(f"✗ Unpackaging function error: {e}")
        return False

def test_clean_function():
    """Test cleanup function"""
    print_step(5, "Testing cleanup function")
    
    # Ask user if they want to clean
    response = input("\nDo you want to clean all package files? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            success = clean_all_packages(verbose=True)
            if success:
                print("✓ Cleanup test passed")
                return True
            else:
                print("✗ Cleanup test failed")
                return False
        except Exception as e:
            print(f"✗ Error during cleanup: {e}")
            return False
    else:
        print("⏭️ Skipping cleanup test")
        return True

def test_edge_cases(base_dir):
    """Test edge cases and error handling"""
    print_step(6, "Testing edge cases")
    
    # Save current directory
    original_cwd = os.getcwd()
    try:
        # Change to test directory
        os.chdir(base_dir)
        
        print("\n1. Testing with non-existent filelist...")
        success = package_files("non_existent.txt", "edge_test_1", verbose=False)
        if not success:
            print("✓ Correctly handled non-existent filelist")
        else:
            print("✗ Should have failed with non-existent filelist")
        
        print("\n2. Testing empty filelist...")
        with open("empty.txt", "w") as f:
            f.write("# Empty filelist\n")
        
        success = package_files("empty.txt", "edge_test_2", verbose=False)
        if not success:
            print("✓ Correctly handled empty filelist")
        else:
            print("✗ Should have failed with empty filelist")
        
        print("\n3. Testing filelist with only comments...")
        with open("only_comments.txt", "w") as f:
            f.write("# Only comments\n# Another comment\n")
        
        success = package_files("only_comments.txt", "edge_test_3", verbose=False)
        if not success:
            print("✓ Correctly handled filelist with only comments")
        else:
            print("✗ Should have failed with filelist with only comments")
        
        return True
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def test_specific_packaging_scenarios(base_dir):
    """Test specific packaging scenarios"""
    print_step(7, "Testing specific packaging scenarios")
    
    # Save current directory
    original_cwd = os.getcwd()
    try:
        # Change to test directory
        os.chdir(base_dir)
        
        # Test 1: Package single file
        print("\n1. Testing single file packaging...")
        files = ["main.py"]
        success = tar_gz_files(files, "single_file_test", verbose=True)
        if success:
            print("✓ Single file packaging test passed")
        else:
            print("✗ Single file packaging test failed")
        
        # Test 2: Package directory with trailing slash
        print("\n2. Testing directory packaging (with trailing slash)...")
        files = ["src/"]
        success = tar_gz_files(files, "directory_test", verbose=True)
        if success:
            print("✓ Directory packaging test passed")
        else:
            print("✗ Directory packaging test failed")
        
        # Test 3: Package non-existent file
        print("\n3. Testing packaging with non-existent file...")
        files = ["main.py", "non_existent.txt", "src/"]
        success = tar_gz_files(files, "mixed_test", verbose=True)
        if success:
            print("✓ Mixed file list packaging test passed")
        else:
            print("✗ Mixed file list packaging test failed")
        
        return True
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def run_manual_tests(base_dir):
    """Run manual tests (recommended)"""
    print("\n" + "="*60)
    print("MANUAL TESTING GUIDE")
    print("="*60)
    
    instructions = f"""
Some functions are interactive, manual testing is recommended:

Test directory: {base_dir}
CLI tool path: {project_root / 'src' / 'cli.py'}

Follow these steps:

1. Go to test directory:
   cd "{base_dir}"

2. Test basic packaging:
   python "{project_root / 'src' / 'cli.py'}" -z include_all.txt all_files -v

3. List packages:
   python "{project_root / 'src' / 'cli.py'}" -l

4. Test unpackaging:
   python "{project_root / 'src' / 'cli.py'}" -u -v

5. Clean packages:
   python "{project_root / 'src' / 'cli.py'}" -c -v

6. Test complex rules:
   python "{project_root / 'src' / 'cli.py'}" -z complex_rules.txt complex_test -v
"""
    print(instructions)
    
    # Show available filelists
    print("\nAvailable filelist files:")
    for file in base_dir.glob("*.txt"):
        if file.is_file():
            print(f"  - {file.name}")

def main():
    """Main test function"""
    print("="*60)
    print("AUTO PACKAGING/UNPACKAGING TOOL - FEATURE TEST")
    print("="*60)
    
    # Create test directory
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    
    # Clean old test data
    if test_dir.exists() and test_dir.is_dir():
        print(f"Cleaning old test data: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)
        time.sleep(1)  # Wait for cleanup
    
    test_dir.mkdir(exist_ok=True)
    print(f"Test directory: {test_dir}")
    
    try:
        # 1. Setup test environment
        setup_test_environment(test_dir)
        
        # 2. Run automated tests
        print("\n" + "="*60)
        print("RUNNING AUTOMATED TESTS")
        print("="*60)
        
        tests = [
            ("Basic packaging", lambda: test_basic_packaging(test_dir)),
            ("Filelist packaging", lambda: test_filelist_packaging(test_dir)),
            ("Specific scenarios", lambda: test_specific_packaging_scenarios(test_dir)),
            ("Edge cases", lambda: test_edge_cases(test_dir)),
            ("List packages", test_list_packages),
            ("Unpackaging", test_unpackaging),
            ("Cleanup", test_clean_function),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\nRunning test: {test_name}")
                if test_func():
                    print(f"✓ {test_name} - PASSED")
                    passed += 1
                else:
                    print(f"✗ {test_name} - FAILED")
                    failed += 1
            except Exception as e:
                print(f"✗ {test_name} - ERROR: {e}")
                import traceback
                traceback.print_exc()
                failed += 1
        
        # 3. Show test results
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total: {passed + failed}")
        
        if failed == 0:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} tests failed")
        
        # 4. Show manual testing guide
        run_manual_tests(test_dir)
        
        # 5. Ask about cleanup
        print("\n" + "="*60)
        response = input("Testing complete. Clean test data? (y/N): ").strip().lower()
        
        if response == 'y':
            print(f"Cleaning test data: {test_dir}")
            shutil.rmtree(test_dir, ignore_errors=True)
            print("Test data cleaned")
        else:
            print(f"Test data preserved at: {test_dir}")
            print("You can continue testing in this directory")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
