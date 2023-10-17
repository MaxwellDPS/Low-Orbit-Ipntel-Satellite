#----------------------------------------------------------------------------------------------------------------------
# Docker low_orbit_intel_satellite v1
#----------------------------------------------------------------------------------------------------------------------
FROM python:3.11-alpine

#----------------------------------------------------------------------------------------------------------------------
# SET DEFAULTS
#----------------------------------------------------------------------------------------------------------------------

ARG APP_USER=low_orbit_intel_satellite
ARG APP_UID=69
ARG CODE_DIR=/opt/low_orbit_intel_satellite

#----------------------------------------------------------------------------------------------------------------------
# Setup User / Group
#----------------------------------------------------------------------------------------------------------------------
RUN addgroup -g ${APP_UID} ${APP_USER} && \
  adduser --ingroup ${APP_USER} -D -u ${APP_UID} --home ${CODE_DIR} -s /bin/bash ${APP_USER}

#----------------------------------------------------------------------------------------------------------------------
# Setup working dir
#----------------------------------------------------------------------------------------------------------------------
WORKDIR ${CODE_DIR}
RUN mkdir ${CODE_DIR}/static && \
  mkdir ${CODE_DIR}/staticfiles && \
  mkdir ${CODE_DIR}/geofiles

#----------------------------------------------------------------------------------------------------------------------
# Install Deps
#----------------------------------------------------------------------------------------------------------------------

# Install packages needed to run your application (not build deps):
RUN apk update && apk add \
  python3-dev \
  ca-certificates \
  py3-maxminddb \
  py3-maxminddb-pyc \
  libmaxminddb \
  libmaxminddb-libs \
  libmaxminddb-dev \
  sudo \
  bash

# Install Build Deps
RUN apk add alpine-sdk

#----------------------------------------------------------------------------------------------------------------------
# Install Build libs
#----------------------------------------------------------------------------------------------------------------------
# Copy in your requirements file
COPY src/requirements.txt /tmp/requirements.txt

#----------------------------------------------------------------------------------------------------------------------
# Install Python Packages
#----------------------------------------------------------------------------------------------------------------------
# Update PIP or risk the wrath of the python 
# Install our packages and hope it dosent catch fire
# get rid of our requirements file, I didnt like him anyhow
RUN  sudo --user=${APP_USER} sh -c 'python -m pip install --upgrade pip --no-cache-dir && \
  # python -m pip install --no-cache-dir "setuptools<58" && \
  python -m pip install --upgrade --no-cache-dir -r /tmp/requirements.txt'

#----------------------------------------------------------------------------------------------------------------------
# Remove Build libs
#----------------------------------------------------------------------------------------------------------------------
# Tell apk not to be a horder and trash that build junk
RUN apk del alpine-sdk sudo && \
  rm /tmp/requirements.txt

#----------------------------------------------------------------------------------------------------------------------
# Copy Code & primary files
# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
#----------------------------------------------------------------------------------------------------------------------
# Copy the main codebase
COPY src/ ${CODE_DIR}/

#----------------------------------------------------------------------------------------------------------------------
# Set for Sekurity
#----------------------------------------------------------------------------------------------------------------------
RUN chown -R ${APP_USER}:${APP_USER} ${CODE_DIR}/* && \
  chmod -R 540 ${CODE_DIR}/* && \
  chmod -R 774 ${CODE_DIR}/static && \
  chmod -R 774 ${CODE_DIR}/staticfiles && \
  chmod -R 770 ${CODE_DIR}/geofiles


# Change to a non-root user - Beacuse we dont want anybody being naughty if they ever manage to get in ;P
USER ${APP_USER}:${APP_USER}

#----------------------------------------------------------------------------------------------------------------------
# Set launch config
#----------------------------------------------------------------------------------------------------------------------
# Define Static files volume
VOLUME ${CODE_DIR}/static
VOLUME ${CODE_DIR}/geofiles

# Expose the UWSGI TCP socket - this way Nginx can do all the hard work
EXPOSE 40269

# Add local pip to bin
ENV PATH="${PATH}:${CODE_DIR}/.local/bin"

# Start uWSGI
CMD ["uwsgi", "--show-config"]