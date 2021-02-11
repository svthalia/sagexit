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

- a `users` app that hooks the built-in Django user model to OpenID (specifically the rather 
  undocumented and outdated version of the Faculty of Science), which is a very stripped down version 
  of the one of https://github.com/KiOui/TOSTI.
- a `room_reservations` app that is a copy of the one on https://github.com/GipHouse/Website to 
  do the actual reservations (but with some minor changes)
- the CI/CD is copied from https://github.com/GipHouse/Website as well. It requires these secrets:
  - `SSH_USER`
  - `SSH_PRIVATE_KEY`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_NAME`
  - `DJANGO_SECRET_KEY`
  - `DJANGO_OPENID_SUPERUSER_USERNAME`

# Set up server
1. `sudo apt install docker-compose`
2. `sudo systemctl enable docker`
3. `sudo usermod -aG docker ubuntu`
4. Run the deployment workflow



NB: with either `apt` or `brew`, `xmlsec1` must also be installed manually!