This is the backend for SaveOurFaves.org.

It's a fairly straightforward Django app with Postgres/PostGIS backing it for the 'nearby' queries. You'll also need [the React frontend](https://github.com/mikeyk/saveourfaves-frontend). It also uses `nginx` as the load balancer and file server for the static files/React app.

To get this up and running:
* Install Docker on your machine
* Either generate certificates using `letsencrypt` and put the results of `/etc/letsencrypt` in a directory above this one called `certificates` (eg `../certificates/letsencrypt/` or edit `nginx/nginx.conf` to remove the HTTPS/letsencrypt references
* Generate an `htpasswd` formatted file and place it in `../certificates/nginx_auth` (this is used to password-protect the Django admin site; there’s also Django’s standard auth there, but this adds another optional layer.
* From the root folder, run `docker-compose up -d`  to bring up `nginx` and `Django`
* From the `db` folder, run `docker-compose up -d` to bring up `Postgres`
* You’ll want to edit the `nginx/nginx.conf` file to match the hostname you’re trying to deploy to. To quickly test if this is all working on your local machine, you can add an `/etc/hosts` line to temporarily point your browser to the locally running nginx instance:
	* eg  `127.0.0.1 saveourfaves.org`

At this point you should have a running Django instance on `localhost:8000`. You should then create at least one `Area` object (for example, in the Bay Area, that represents SF vs East Bay vs South Bay), a few `Neighborhood`  objects inside each `Area`, and then add some `Places` to each `Neighborhood`. Once you’ve done all of that, you can run:

```
# log into the Docker container running Django
docker exec -it <name of Django container> /bin/bash
cd /usr/local/site
python scripts/dump_neighborhoods.py Neighborhoods.js
python scripts/dump_places.py Places.js
```

At that point, you can copy the `Neighborhoods.js` and `Places.js` files into the saveourfaves-frontend repository; use them to overwrite the ones in `src/CityData/`. You’ll also want to update `src/CityData/Areas.js` with information about your areas.