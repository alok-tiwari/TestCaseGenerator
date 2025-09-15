from setuptools import setup, find_packages

setup(
    name="TestCaseGenerator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "python-dotenv",
        "tenacity",
    ],
    python_requires=">=3.8",
)