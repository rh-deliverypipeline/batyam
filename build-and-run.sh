#!/bin/bash

IMG=${IMG:-'test'}
docker build . -t ${IMG}
docker run --rm -it ${IMG}
