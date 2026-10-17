# syntax=docker/dockerfile:1.7

# Keep local Apple Silicon runs and the amd64 CI runner on the same JVM image.
FROM eclipse-temurin:21-jre-jammy@sha256:468586c92d39f8cbad76574623db3fe001625ed4d895431c3ff7bd2ec9ce7ae3

ARG FREEROUTING_VERSION=2.1.0
ARG FREEROUTING_SHA256=2c07d58f75dac03782664081e7a58b41c25400d871a9fcf166a2ea6fe60d5def

ADD --checksum=sha256:${FREEROUTING_SHA256} \
  https://github.com/freerouting/freerouting/releases/download/v${FREEROUTING_VERSION}/freerouting-${FREEROUTING_VERSION}.jar \
  /opt/freerouting.jar

WORKDIR /work

ENTRYPOINT ["java", "-jar", "/opt/freerouting.jar"]
