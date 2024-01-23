FROM node:20 as build

SHELL ["/bin/bash", "-c"]

RUN npm i -g pnpm

RUN apt-get update && apt-get install -y \
        zip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -s "https://get.sdkman.io" | /bin/bash
RUN chmod a+x /root/.sdkman/bin/sdkman-init.sh
RUN source "/root/.sdkman/bin/sdkman-init.sh" \
    && sdk install java 21.0.2-tem \
    && sdk install sbt

WORKDIR /lila

COPY . .

RUN source "/root/.sdkman/bin/sdkman-init.sh" \
    && ui/build \
    && ./lila dist \
    && unzip target/universal/lila-4.0.zip

# ############################################

FROM eclipse-temurin

WORKDIR /lila

COPY --from=build /lila/lila-4.0 .
COPY --from=build /lila/public ./public
COPY ./conf/logger.dev.xml ./conf/logger.dev.xml

CMD ["./bin/lila"]
