# Start from a standard Ubuntu Linux computer.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install all the extra tools Flutter needs to build apps.
# We are including 'adb' here for Android development.
RUN sudo apt-get update && sudo apt-get install -y \
    curl \
    git \
    unzip \
    libglu1-mesa \
    xz-utils \
    zip \
    clang \
    cmake \
    ninja-build \
    pkg-config \
    libgtk-3-dev \
    adb

# Use the 'vscode' user that the base image provides.
USER vscode

# Download the Flutter software into our cloud computer.
RUN git clone https://github.com/flutter/flutter.git --depth 1 --branch 3.22.2 /home/vscode/flutter

# Tell the terminal where to find the 'flutter' command.
ENV PATH="/home/vscode/flutter/bin:${PATH}"

# Download all the necessary parts of Flutter so it's ready to go.
RUN flutter precache

# Automatically accept the Android licenses.
RUN yes | flutter doctor --android-licenses
