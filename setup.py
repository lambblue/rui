from setuptools import setup, find_packages

setup(
    name="rui",
    version="1.0.0",
    description="Real User Instruction (RUI) - Prompt-Level Instruction Authentication for LLM Agents",
    author="RUI Team",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
