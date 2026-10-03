# Jenkins with the extra tools our pipeline needs (python + docker cli)
FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

# only the docker client is needed, the daemon is the host's (socket is mounted)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker

# stays root so it can use the mounted docker socket - fine for a local lab setup,
# not something to do on a real shared Jenkins server
