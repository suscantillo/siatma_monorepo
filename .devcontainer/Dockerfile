# Start from a standard Ubuntu Linux computer.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install all system dependencies in one go
# ADDED: wget, unzip, and a Java Development Kit (JDK) for the Android toolchain
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
    adb \
    openjdk-17-jdk

# Switch to the non-root 'vscode' user for security and permissions
USER vscode
WORKDIR /home/vscode

# --- Setup Android SDK ---
# 1. Set environment variables that Android tools and Flutter will need
ENV ANDROID_SDK_ROOT="/home/vscode/android-sdk"
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH="${PATH}:${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools"

# 2. Install the Android Command-Line Tools
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O android-sdk.zip && \
    unzip -q android-sdk.zip -d ${ANDROID_SDK_ROOT}/cmdline-tools && \
    mv ${ANDROID_SDK_ROOT}/cmdline-tools/cmdline-tools ${ANDROID_SDK_ROOT}/cmdline-tools/latest && \
    rm android-sdk.zip

# --- Setup Flutter ---
# 1. Clone the Flutter SDK
RUN git clone https://github.com/flutter/flutter.git --depth 1 --branch 3.22.2 /home/vscode/flutter

# 2. Add Flutter's commands to the PATH
ENV PATH="/home/vscode/flutter/bin:${PATH}"

# 3. Explicitly tell Flutter where to find the Android SDK
RUN flutter config --android-sdk ${ANDROID_SDK_ROOT}

# 4. Download all of Flutter's own tools and dependencies
RUN flutter precache

# 5. Use the Android SDK's own tool to accept all licenses. This is more reliable.
RUN yes | sdkmanager --licenses

# 6. Run a final diagnostic check to ensure everything is perfect.
RUN flutter doctor -v
