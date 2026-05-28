FROM python:3.12-slim

LABEL maintainer="Elder Bernardi"
LABEL description="Exocórtex.IA Provisioner — Hermes Agent + Golden Image"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git bash jq \
    && rm -rf /var/lib/apt/lists/*

# Install Hermes Agent via official script
RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash \
    || pip install hermes-agent

# Prepare directories
RUN mkdir -p /opt/data /opt/secrets /workspace

ENV HERMES_HOME=/opt/data
WORKDIR /workspace

# Copy the full PDD v2 artifacts and provisioner
COPY plans/pdd_v2/artifacts/ /workspace/artifacts/
COPY plans/pdd_v2/provisioner/ /workspace/provisioner/

# Make scripts executable
RUN chmod +x /workspace/provisioner/lib/*.sh \
    /workspace/provisioner/docker/entrypoint.sh 2>/dev/null || true

ENTRYPOINT ["/workspace/provisioner/docker/entrypoint.sh"]
