"""
Setup script for Mix Readiness AI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().splitlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name="mix-readiness-ai",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered Logic Pro session preparation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mix-readiness-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'mix-readiness=src.mix_readiness_engine:main',
            'mix-readiness-gui=src.ui.control_panel:main',
        ],
    },
    include_package_data=True,
    package_data={
        'mix_readiness': [
            'config/*.yaml',
            'models/*',
            'presets/*',
        ],
    },
)
