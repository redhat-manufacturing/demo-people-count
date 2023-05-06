FROM registry.access.redhat.com/ubi9/ubi

LABEL name="Retail - People Count Monolith" \
      vendor="Guise AI" \
      version="1.0.0" \
      release="1" \
      summary="People Count " \
      description="Retail Edge with People Count is a ML \
application to provide insights on the extry and exit of \
people in a facility as well as head count."

RUN yum update -y
RUN yum install -y python3 python3-pip python3-devel g++

WORKDIR /app
COPY . /app
COPY application/licenses/ /licenses/
ENV LD_LIBRARY_PATH=/app/application/lib_rlm:$LD_LIBRARY_PATH

RUN pip install --upgrade pip setuptools urllib3==1.26.5
RUN pip install install Cython
RUN pip install install numpy
RUN pip install wheel
RUN pip install lap
RUN pip install -r requirements.txt
RUN pip install opencv-python-headless
EXPOSE 5041
CMD ["python3","./run.pyc"]
