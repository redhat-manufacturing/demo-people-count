# People_count_monolith 

## Getting Started
- [Podman introduction](https://docs.google.com/document/d/1xCdkYFhxJZ0CFcx8qAWM4bllG80WI3mCfBJfB-kdIKI/edit?usp=sharing)

## How to run quay images

```sh
 $ podman volume create people-count-storage
 $ podman login quay.io
 $ podman pull quay.io/guiseai_retail/apparel-logo:latest
 $ podman run --name apparel-logo-container \
  -p 5041:5041 \
  -v apparel-logo-storage:/app/ \
  -d quay.io/guiseai_retail/apparel-logo:latest
```

## 1. Initial setup

```sh
 $ cd people-count-monolith-podman
 $ sh setup.sh
```

## 2. build and run the image using podman:
1. build the image
```sh
 podman build -t people_count .
```

2. run the image
```sh
 podman run people_count
```

## 3. build and run the image using podman-compose:

To start
```sh
 podman-compose up
```

To stop
```sh
 podman-compose down
```
