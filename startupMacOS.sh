#!/bin/bash

# Check if Docker is installed, if not install it
if command -v docker &> /dev/null; then
    echo "Docker is installed."
    docker_version=$(docker --version)
    echo "Docker version: $docker_version"
else
    echo "Docker is not found. Installing now."

    # Check if Homebrew is installed, if it is, install docker
    if command -v brew &> /dev/null; then
        install_docker_macos
    else
        echo "Homebrew not found. Please install Homebrew first from https://brew.sh/, then run the script again."
    fi
fi

# Check if Docker Compose is installed, if not install it
if command -v docker-compose &> /dev/null; then
    echo "Docker Compose is already installed."
else
    echo "Docker Compose not found. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
fi

echo "Starting application containers."
docker-compose -f docker-compose.yaml up -d

# Function to install Docker on macOS using Homebrew
install_docker_macos() {
    # Install Homebrew (if not installed)
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Install Docker using Homebrew
    brew install --cask docker

    # Start Docker Desktop (if not already running)
    open --background -a Docker

    # Wait for Docker to be ready (you may need to adjust the sleep time based on your system's speed)
    sleep 10

    # Add your user to the 'docker' group (optional but recommended to avoid using 'sudo' with Docker)
    sudo dscl . append /Groups/docker GroupMembership $(whoami)

    # Restart the shell to apply the group membership changes (you can also log out and log back in)
    exec bash
}
