===============================================================================
  Nd2Fe14B Magnetization Curve Fitting and Interactive Tool
===============================================================================

This program provides a graphical interface to fit and compute the temperature-
dependent saturation magnetization of Nd2Fe14B, with interactive query support.

REQUIREMENTS
===============================================================================
- Python version: 3.13.3 (strictly recommended)
- OS: Windows, macOS, or Linux

If your Python version is not 3.13.3, please upgrade to this exact version
using pyenv, conda, or the official Python installer.

GETTING STARTED
===============================================================================

1. Clone the repository
   git clone https://github.com/your-username/your-repo.git
   cd your-repo

2. (Recommended) Create a virtual environment with Python 3.13.3
   python3.13 -m venv venv
   # Activate it:
   # Windows: venv\Scripts\activate
   # Linux/macOS: source venv/bin/activate

3. Install dependencies from the local "library" folder (offline)
   All required wheels (numpy, scipy, matplotlib and their dependencies)
   are pre-downloaded and placed in the "library" directory.

   Run:
   pip install --no-index --find-links library -r library/requirements.txt

   Note: The file library/requirements.txt contains the list of packages.

4. Run the program
   python your_program.py   (replace with actual main script name)

TROUBLESHOOTING
===============================================================================

Q: My Python version is not 3.13.3. What should I do?
A: Install Python 3.13.3 using pyenv, conda, or the official installer.
   Alternatively, you can delete the "library" folder and re-download the
   packages for your own Python version (requires internet connection):
       pip download --dest library numpy scipy matplotlib

Q: I get "tkinter not found" error.
A: tkinter is part of the standard library, but on some Linux distributions
   it must be installed separately:
       Ubuntu/Debian: sudo apt install python3-tk
       Fedora: sudo dnf install python3-tkinter
   Windows/macOS usually include tkinter by default.

Q: The wheels in "library" are not compatible with my platform.
A: The pre-downloaded wheels are for Python 3.13.3 on Windows (most common).
   If you are on Linux/macOS or a different Python version, delete the
   "library" folder and re-download the packages for your environment using
   the pip download command above.

COPYRIGHT AND INFRINGEMENT NOTICE
===============================================================================
This software is provided for non-commercial, educational, and research
purposes only. It is not intended for any commercial use.

If any part of this software or its documentation infringes upon existing
copyrights, trademarks, or other intellectual property rights, please contact
the repository owner immediately. Upon verification of a valid infringement
claim, the affected material will be removed or modified promptly.

By using this software, you agree that the maintainers are not liable for
any unintentional copyright violations, and you accept that the software may
be taken down or changed at any time without prior notice if required by law
or rights holders.

LICENSE
===============================================================================
(Specify your license here, e.g., MIT, GPL, etc. – ensure it is compatible
with non-commercial use if you add restrictions.)

CONTACT
===============================================================================
(Optional)
