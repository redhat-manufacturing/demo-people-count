# People_Count_Monolith 

## Getting Started
- [Podman introduction](https://docs.google.com/document/d/1xCdkYFhxJZ0CFcx8qAWM4bllG80WI3mCfBJfB-kdIKI/edit?usp=sharing)
- Podman storage: we use the podman storage as a backup to our logs and database.

# Here are the 3 ways to start the pipeline

## 1. Run Quay Image

No need to clone github repo

```sh
 $ podman login quay.io
 $ podman volume create people-count-storage
 $ podman pull quay.io/guiseai_retail/people-count:ob_1.0.1_ovino
 $ podman run --name people-count-container \
  -p 5041:5041 \
  -v people-count-storage:/app/ \
  -d quay.io/guiseai_retail/people-count:ob_1.0.1_ovino
```

## 2. Build image locally and run it using podman commands

clone the repo
```sh
 $ git clone https://github.com/GuiseAI/people-count-monolith.git
 $ cd people-count-monolith
 $ git checkout <branch_name>
```

1. build the image and create storage
```sh
 $ podman build -t people-count .
 $ podman volume create people-count-storage
```

2. run the image
```sh
 podman run --name people-count-container \
  -p 5041:5041 \
  -v people-count-storage:/app/ \
  -d people-count
```

## 3. Build and run the image using podman-compose:

clone the repo
```sh
 $ git clone https://github.com/GuiseAI/people-count-monolith.git
 $ cd people-count-monolith
 $ git checkout <branch_name>
```

To start
```sh
 podman-compose up
```

To stop
```sh
 podman-compose down
```

# Dashboard

URL to access dashboard = localhost:5041
IP = 127.0.0.1
PORT = 5041
TOKEN = 0 