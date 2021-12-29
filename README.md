# Sagexit

_Even our beloved Mercator could not escape the coronavirus. 
Instead of a cozy space where far too many people, far too close to each other,
trying to study while actually socializing and complaining about the dirt in the kitchen, 
Mercator has become a silent place where people actually come to study (or at least, 
that's what they should be doing)._

Because everything in times of corona needs a registration system, also Mercator had to get one. 
As computer scientists, of course we <s>developed are own one that exactly fits our needs</s> 
searched the whole internet for buggy systems that we did not have to pay for. What we finally
got: sagenda. A terrible system that did not allow cancelling reservations, or didn't even
allow you to look up who actually did a reservation.

**It's time for a sagexit.**

With a lot of inspiration from https://github.com/GipHouse/Website and https://github.com/KiOui/TOSTI, 
I hacked together a rather minimal application (though I would love to get rid of the sass as well).

It features: 

- a `room_reservations` app that is a copy of the one on https://github.com/GipHouse/Website to 
  do the actual reservations (but with some minor changes)
- the CI/CD is copied from https://github.com/GipHouse/Website as well. It requires these secrets:
  - `SSH_USER`
  - `SSH_PRIVATE_KEY`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_NAME`
  - `DJANGO_SECRET_KEY`
  
# Set up server
1. `sudo apt install docker-compose`
2. `sudo systemctl enable docker`
3. `sudo usermod -aG docker ubuntu`
4. Run the deployment workflow

User authentication happens via the CNCZ Science SAML signon server. This server needs to be set up
manually after deployment from the Django admin. It is thus required to create a temporary superuser on
the server, to actually do this. After setup and first login, the superuser permissions can be transferred
to an actual account.


NB: for local development, with either `apt` or `brew`, `xmlsec1` must also be installed manually!

# Set up local development

clone the repo

1. `cd website`
2. `poetry shell` 
3. `poetry install`
   (if any errors come up here you can try to install it yourself with pip install XX)
4. `python manage.py migrate`
5. `python manage.py compilescss`
6. `python manage.py python manage.py collectstatic --no-input -v0 --ignore="*.scss"`
7. `python manage.py runserver`