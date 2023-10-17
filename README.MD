# Low Orbit I(p)ntel Satellite

Opensouce API to run IP lookups for City, ASN, and Country


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
BASE: `/api/v1`
[OpenAPI JSON](docs/openapi.json)

![swagger](docs/swagger.jpg)


### Auth

POST /auth/login/

POST /auth/logout/

POST /auth/logoutall/

POST /auth/refresh/

### Geo Sync
GET /geo/sync

POST /geo/sync

GET /geo/sync/{request_uuid}

DELETE /geo/sync/{request_uuid}

### Lookup Request

GET /lookup/

POST /lookup/create

GET /lookup/list

GET /lookup/{request_uuid}/

DELETE /lookup/{request_uuid}/

GET /lookup/{request_uuid}/results