# Local Dev Env

## Cross Built Docker Images
as we have people on the team using the Apple M1 computer, which runs the
arm64 architecture, we need to be able to run the entire infrastructure both
on AMD64 and ARM64 machines.

In order to test this, docker can make multi arch images by using the `buildx`
docker command. Successful builds with the `buildx` command ensures a good
developer experience -- also for the M1 people.

__Building Keycloak:__ As an example we can cross build the keycloak image
by

1. Navigate to the folder
2. If no builder isntance has previously been created, run
   `docker buildx create --use --platform linux/amd64,linux/arm64`
3. Build for AMD64 and ARM64 `docker buildx build --platform linux/amd64,linux/arm64 .`

_Note:_ this really doesn't do anything but testing that the image can be built
for multiple architectures.

