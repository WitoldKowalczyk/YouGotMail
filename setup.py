from setuptools import setup, find_packages

setup(
    name="yougotmail",
    version="0.0.1",
    description="Easily create AI Agents in MS Outlook",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Witold Kowalczyk",
    author_email="witold@delosintelligence.com",
    url="https://github.com/WitoldKowalczyk/YouGotMail",
    packages=find_packages(),
    include_package_data=True,  # includes files listed in MANIFEST.in (if any)
    install_requires=[
        "requests",
        "python-dotenv",
        "nanoid",
        "boto3",
        "pymongo",
        "markdownify",
        "openai",
        "python-dateutil",
        "bson"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10.12",
)
