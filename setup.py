from setuptools import setup, find_packages

setup(
    name="alfred-organizer",
    version="0.1.0",
    description="Your personal file butler - intelligent file organization",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "watchdog>=3.0.0",
        "pyyaml>=6.0",
        "colorama>=0.4.6",
        "click>=8.1.0",
        "scikit-learn>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "alfred=alfred.cli:main",
        ],
    },
    python_requires=">=3.8",
)
