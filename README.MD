# The wheretf!

Introducing the wheretf! This app is a full Django, DRF, Celery, MySQL, and RabbitMQ Stack. This app features a functional paginated rest API, with full swagger documentation and an OpenAPI Schema.

This app uses a task that runs every 10 mins to check over our "CaptureSource"s, Then if we have meet the minimum time passed since the last scrape, we will use the CaptureSource's regex rule to scrape the Tor IP's and other metadata.

# Dev Setup

1. Edit your `.env` file to meet prod specs
2. Run `docker-compose up --build` (or preferably prebuild and push images to your registry)
4. Sign in with your default user at your hostname at `https://<IP>:8443/admin`
5. Udger and www.dan.me.uk IP's should start to populate automatically within 10 min
6. Go to `https://<IP>:8443/api` to read the swagger docs
7. Go to `https://<IP>:8443/api/?format=openapi` to fetch the OpenAPI schema (This can be imported to Postman)

# Prod Setup

Here is how to run in production with docker-compose. However I personally would put this in kubernetes for prod

1. Edit your `.env` file to meet prod specs
2. Run `docker-compose up --build` (or preferably prebuild and push images to your registry)
3. Point your reverse proxy to `https://<IP>:8443` 
4. Sign in with your default user at your hostname at `https://<your host>/admin`
5. Udger and www.dan.me.uk IP's should start to populate automatically within 10 min
6. Go to `https://<your host>/api` to read the swagger docs
7. Go to `https://<your host>/api/?format=openapi` to fetch the OpenAPI schema (This can be imported to Postman)

## Admin Page Operation

- The Django admin page can be used to create Capture Sources or to Create / Update / Exclude To  Addresses
- The Django admin page also can view, edit, and monitor celery task execution

## Capture Sources

Capture Sources define 4 main things:
- Name  
- URL (The URL to the page with the TOR IPs)
- Regex Match
	- This  must be a regex pattern that uses named groups to capture the data. **The only required group is `ip`**. Any other named groups will be returned via the API
- Enabled 

### The following capture sources have been pre added:
- https://www.dan.me.uk/tornodes
- https://udger.com/resources/ip-list/tor_exit_node

## Tor Addresses
Tor Addresses are the objects that contain the Tor node IPs. These have 2 main elements:
- Excluded field - this hides it from the primary list EP
- Score - I added this as a score value; seems extremely relevant here


## API Endpoints

I took the liberty of making CaptureSources configurable via API, this way the platform is more flexible 
### Tor Addresses
- [GET] `/api/tor_address/` - Endpoint 1 from the request (IP Excluded Filtered List Endpoint)
- [GET] `/api/tor_address/list_all` - Bonus EP (Non-Filtered List Endpoint)
- [GET/POST/DELETE] `/api/tor_address/<IP>/` - Endpoint 2 + some extras 
	- This EP can update to allow excluding via HTTP/POST
	- This EP can return details on a single IP
	- This EP can delete the IP
- [GET/POST/DELETE] `/api/tor_address/uuid/<IP's UUID>/` - Bonus EP 
	- This EP can update to allow excluding via HTTP/POST via UUID
	- This EP can return details on a single IP via UUID
	- This EP can delete the IP via UUID
### Capture Source
- [GET] `/api/capture_source/`
	- Gets a list of all capture sources
- [GET] `/api/capture_source/create`
	- Allows creation of a capture source via API
- [GET/POST/DELETE] `/api/tor_address/<IP>/` - Endpoint 2 + some extras 
	- This EP can update to allow excluding via HTTP/POST
	- This EP can return details on a single IP
	- This EP can delete the IP
- [GET/POST/DELETE] `/api/tor_address/<CaptureSources UUID>/`
	- This EP can update via HTTP/POST via UUID
	- This EP can return details on a single capture source via UUID
	- This EP can delete the capture source via UUID

# Licensing
This application is licensed under AGPLv3 

