# Low Orbit Intel Satellite!

Introducing the low_orbit_intel_satellite! This app is a full Django, DRF, Celery, MySQL, and RabbitMQ Stack. This app features a functional paginated rest API, with full swagger documentation and an OpenAPI Schema.

# Dev Setup

1. Edit your `.env` file to meet prod specs
2. Run `docker-compose up --build` (or preferably prebuild and push images to your registry)
4. Sign in with your default user at your hostname at `https://<IP>:8443/admin`
6. Go to `https://<IP>:8443/api` to read the swagger docs
7. Go to `https://<IP>:8443/api/?format=openapi` to fetch the OpenAPI schema (This can be imported to Postman)

# Prod Setup

Here is how to run in production with docker-compose. However I personally would put this in kubernetes for prod

1. Edit your `.env` file to meet prod specs
2. Run `docker-compose up --build` (or preferably prebuild and push images to your registry)
3. Point your reverse proxy to `https://<IP>:8443` 
4. Sign in with your default user at your hostname at `https://<your host>/admin`
6. Go to `https://<your host>/api` to read the swagger docs
7. Go to `https://<your host>/api/?format=openapi` to fetch the OpenAPI schema (This can be imported to Postman)


## API Endpoints
