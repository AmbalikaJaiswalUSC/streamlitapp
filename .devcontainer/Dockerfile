# Use the latest stable Node.js
# For Windows and Mac users with intel Silicon, use the following line
# FROM node:20.16.0

# For Mac users with Apple Silicon, use the following line instead and comment out the previous line
FROM --platform=linux/amd64 node:20.16.0

# Install Python and necessary dependencies
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y python3.11 python3-pip python3.11-venv

# Install R and RStudio
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    gdebi-core \
    libnss3 \
    libx11-xcb1 \
    libxkbcommon0 && \
    wget https://download1.rstudio.org/electron/jammy/amd64/rstudio-2024.04.2-764-amd64.deb && \
    gdebi -n rstudio-2024.04.2-764-amd64.deb

# Clean up APT when done
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Git
RUN apt-get update && apt-get install -y git

# Install zsh
RUN apt-get update && apt-get install -y zsh

# Install Oh My Zsh
RUN curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh | sh

# Set custom prompt in .zshrc
RUN sed -i 's/^ZSH_THEME=".*"/ZSH_THEME="robbyrussell"/' ~/.zshrc && \
    echo 'PROMPT="%{$fg_bold[cyan]%}DSCI554 %{$fg_no_bold[blue]%}%~ %{$reset_color%}%% "' >> ~/.zshrc

# Set zsh as the default shell
RUN chsh -s /bin/zsh

# Create and activate the Python virtual environment
RUN python3.11 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Upgrade pip and install Python packages in the virtual environment
RUN pip install --upgrade pip
RUN pip install notebook ipykernel

# Install IPython kernel in the virtual environment
RUN python -m ipykernel install --prefix=/app/venv --name=python3

# Expose necessary ports
EXPOSE 2000 3000 5173 5500 8501

# Default command (optional)
CMD ["zsh"]
