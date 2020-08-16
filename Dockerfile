# For more information, please refer to https://aka.ms/vscode-docker-python
FROM lifoid

# Install application
WORKDIR /app
ADD . /app
RUN pip install -e .

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser
