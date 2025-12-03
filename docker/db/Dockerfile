ARG POSTGRES_DB=cne
ARG POSTGRES_USER=postgres
ARG POSTGRES_PASSWORD=kzwip43
ARG RESTORE_SH=/docker-entrypoint-initdb.d/restore.sh
ARG BASEOSM_DUMP=/docker-entrypoint-initdb.d/baseOSM.dump

FROM harbor.prd.afip.gob.ar/dockerhub/pgrouting/pgrouting:16-3.5-3.8 AS builder

ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG RESTORE_SH
ARG BASEOSM_DUMP

WORKDIR /root

COPY ./data/ .
RUN cat baseOSM.dump.parta* > ${BASEOSM_DUMP}

COPY entrypoints/restore.sh ${RESTORE_SH}
RUN chmod +x ${RESTORE_SH}

# Avoid to start the PostgreSQL daemon (we don’t need it on this step)
# RUN ["sed", "-i", "s/exec \"$@\"/echo \"skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]
# RUN /usr/local/bin/docker-entrypoint.sh postgres

####################################################################
# FROM harbor.prd.afip.gob.ar/dockerhub/pgrouting/pgrouting:16-3.5-3.8

# # Copy the initialized data from the builder stage
# COPY --from=builder /var/lib/postgresql/data /var/lib/postgresql/data
