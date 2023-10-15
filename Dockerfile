#----------------------------------------------------------------------------------------------------------------------
# Docker wheretf v1
#----------------------------------------------------------------------------------------------------------------------
FROM python:3.11

#----------------------------------------------------------------------------------------------------------------------
# Create Users / Groups
#----------------------------------------------------------------------------------------------------------------------

# Create a group and user to run our app
ARG APP_USER=wheretf
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

#----------------------------------------------------------------------------------------------------------------------
# Install Deps
#----------------------------------------------------------------------------------------------------------------------

# Install packages needed to run your application (not build deps):
#   mime-support -- for mime types when serving static files
# We need to recreate the /usr/share/man/man{1..8} directories first because
# they were clobbered by a parent image.
RUN seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} 
RUN apt-get update && do add-apt-repository ppa:maxmind/ppa
RUN apt-get update && apt-get install -y --no-install-recommends mime-support \
    python3-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    xmlsec1 \     
    libxmlsec1-dev \
    nano \
    net-tools \
    ca-certificates \
    dnsutils \
    libmaxminddb0 \
    libmaxminddb-dev \
    mmdb-bin
     
#----------------------------------------------------------------------------------------------------------------------
# Install BUILD DEPS & INSTALL pip DEPS
#----------------------------------------------------------------------------------------------------------------------
# Copy in your requirements file
COPY src/requirements.txt /tmp/requirements.txt

# Install Build Deps
RUN apt-get install -y --no-install-recommends build-essential pkg-config

# Update PIP or risk the wrath of the python 
# Install our packages and hope it dosent catch fire
# get rid of our requirements file, I didnt like him anyhow
RUN python -m pip install --upgrade pip --no-cache-dir && \
  pip install --upgrade --no-cache-dir -r /tmp/requirements.txt && \
  rm /tmp/requirements.txt

# Tell apt not to be a horder and trash that build junk
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false  build-essential pkg-config && \
  rm -rf /var/lib/apt/lists/*

#----------------------------------------------------------------------------------------------------------------------
# Copy Code & primary files
#----------------------------------------------------------------------------------------------------------------------

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /code/
WORKDIR /code/

# Copy the main codebase
COPY src/ /code/
RUN mkdir /code/static
RUN mkdir /code/staticfiles

# Fix code dir perms
# pyO365 fix https://github.com/O365/python-o365/blob/7bab7798c7d952c47a089878fed0630466ea7fb9/tests/run_tests_notes.txt#L8
RUN chown -R ${APP_USER}:${APP_USER} /code/ && \
  chmod -R 540 /code/ && \
  chmod -R 740 /code/static && \
  rm /code/requirements.txt

#----------------------------------------------------------------------------------------------------------------------
# Run Prod  prep tasks
#----------------------------------------------------------------------------------------------------------------------
# Change to a non-root user - Beacuse we dont want anybody being naughty if they ever manage to get in ;P
USER ${APP_USER}:${APP_USER}

# Define Static files volume
VOLUME /code/static

# Expose the UWSGI TCP socket - this way Nginx can do all the hard work
EXPOSE 41654

# Start uWSGI
CMD ["uwsgi", "--show-config"]