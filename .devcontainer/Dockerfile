FROM mcr.microsoft.com/devcontainers/base:latest

USER vscode

# Install mise
RUN curl -fsSL https://mise.run | sh \
    && echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc \
    && echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
