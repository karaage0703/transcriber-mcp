from setuptools import setup, find_packages

setup(
    name="transcriber_mcp",
    version="0.1.0",
    description="A MCP server for transcribing audio and video files to text",
    author="Transcriber MCP Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "faster-whisper",
        "mcp[cli]",  # MCPプロトコル実装
        "ffmpeg-python",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
)
