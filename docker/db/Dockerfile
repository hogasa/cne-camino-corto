FROM pgrouting/pgrouting:16-3.5-3.8 AS builder

ARG RESTORE_SH
ARG BASEOSM_DUMP

WORKDIR /root

COPY ./data/ .
RUN cat baseOSM.dump.parta* > ${BASEOSM_DUMP}

COPY entrypoints/restore.sh ${RESTORE_SH}
RUN chmod +x ${RESTORE_SH}
