import subprocess
import os
import sys

edge_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

browser_exe = None
for p in edge_paths:
    if os.path.exists(p):
        browser_exe = p
        break

if not browser_exe:
    print("Browser executable not found!")
    sys.exit(1)

print(f"Using browser: {browser_exe}")

files = [
    (
        r"d:\Placement\Literature_Review_MCA306.html",
        r"d:\Placement\Literature_Review_MCA306.pdf",
    ),
    (
        r"d:\Placement\System_Design_Proposed_Model_MCA306.html",
        r"d:\Placement\System_Design_Proposed_Model_MCA306.pdf",
    ),
]

for html_file, pdf_file in files:
    if not os.path.exists(html_file):
        print(f"HTML not found: {html_file}")
        continue
    
    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file}",
        html_file,
    ]
    print(f"Generating: {pdf_file} ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
        print(f"SUCCESS: {pdf_file} ({os.path.getsize(pdf_file)} bytes)")
    else:
        print(f"FAILED: {pdf_file}")
        if res.stderr:
            print("Error:", res.stderr)

print("Done!")
