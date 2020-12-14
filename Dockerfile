FROM registry.access.redhat.com/ubi8/python-36
LABEL "io.openshift.s2i.build.image"="registry.access.redhat.com/ubi8/python-36" \
      "io.openshift.s2i.build.commit.author"="Omer Amsalem <oamsalem@redhat.com>" \
      "io.openshift.s2i.build.commit.date"="Tue Nov 17 10:14:04 2020 +0200" \
      "io.openshift.s2i.build.commit.id"="22ffeb59aedfb1637c55244b3bc2638f5dd4177d" \
      "io.openshift.s2i.build.commit.ref"="georgettica/add-dockerfile" \
      "io.openshift.s2i.build.commit.message"="Change ssl verification to False" \
      "io.openshift.s2i.build.source-location"="."

USER root
# Copying in source code
COPY . /tmp/src
# Change file ownership to the assemble user. Builder image must support chown command.
RUN chown -R 1001:0 /tmp/src
USER 1001
# Assemble script sourced from builder image based on user input or image metadata.
# If this file does not exist in the image, the build will fail.
RUN /usr/libexec/s2i/assemble
# Run script sourced from builder image based on user input or image metadata.
# If this file does not exist in the image, the build will fail.
CMD /usr/libexec/s2i/run
