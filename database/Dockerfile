FROM postgres:13

ENV POSTGRES_USER=admin
ENV POSTGRES_DB=mydatabase

COPY create_table.sql /docker-entrypoint-initdb.d/

EXPOSE 5432