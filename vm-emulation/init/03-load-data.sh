#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
\copy public.buildings(id, build_year, building_type_int, latitude, longitude, ceiling_height, flats_count, floors_total, has_elevator) FROM '/data/sp_1_project_buildings_202402291420.csv' WITH (FORMAT csv, HEADER true)
\copy public.flats(id, floor, is_apartment, kitchen_area, living_area, rooms, studio, total_area, price, building_id) FROM '/data/sp_1_project_flats_202402291420.csv' WITH (FORMAT csv, HEADER true)
EOSQL
