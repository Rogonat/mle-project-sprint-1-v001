DROP TABLE if exists public.buildings;

CREATE TABLE public.buildings (
    id int8 NULL,
    build_year int8 NULL,
    building_type_int int8 NULL,
    latitude float8 NULL,
    longitude float8 NULL,
    ceiling_height float8 NULL,
    flats_count int8 NULL,
    floors_total int8 NULL,
    has_elevator bool NULL
);
CREATE INDEX ix_buildings_id ON public.buildings USING btree (id);

-- COPY public.buildings(id, build_year, building_type_int, latitude, longitude, ceiling_height, flats_count, floors_total, has_elevator) FROM 'sp_1_project_buildings_202402291420.csv' WITH (FORMAT csv, HEADER true);
