# Start from a standard Ubuntu Linux computer.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install all the extra tools Flutter needs to build apps.
# We are including 'adb' here for Android development, plus 'wget' and 'unzip'.
RUN sudo apt-get update && sudo apt-get install -y \
    curl \
    git \
    wget \
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
WORKDIR /home/vscode

# Set environment variable for Android SDK root
ENV ANDROID_SDK_ROOT="/home/vscode/android-sdk"

# --- NEW: Install Android Command-Line Tools ---
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O android-sdk.zip && \
    unzip -q android-sdk.zip -d ${ANDROID_SDK_ROOT}/cmdline-tools && \
    mv ${ANDROID_SDK_ROOT}/cmdline-tools/cmdline-tools ${ANDROID_SDK_ROOT}/cmdline-tools/latest && \
    rm android-sdk.zip

# Add Flutter and the new Android SDK tools to the PATH.
# This MUST come after the installations.
ENV PATH="/home/vscode/flutter/bin:${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${PATH}"

# Download the Flutter software into our cloud computer.
RUN git clone https://github.com/flutter/flutter.git --depth 1 --branch 3.22.2 /home/vscode/flutter

# Download all the necessary parts of Flutter so it's ready to go.
RUN flutter precache

# --- NOW THIS WILL WORK ---
# Automatically accept the Android licenses.
RUN yes | flutter doctor --android-licenses

# Final check
RUN flutter doctor -v
# Download all the necessary parts of Flutter so it's ready to go.
RUN flutter precache

# Automatically accept the Android licenses.
RUN yes | flutter doctor --android-licenses
