# JVM build: the 2.5.0 native CLI omits serialization metadata for board items.
FROM eclipse-temurin:25-jre@sha256:dbb43d81099eec91e0800226ed2296d03146ee7857165b95112372ad0d67e87f
ADD --checksum=sha256:f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7 \
  https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar \
  /opt/freerouting.jar
WORKDIR /work
ENTRYPOINT ["java", "-Xmx6g", "-jar", "/opt/freerouting.jar"]
