DROP TABLE if exists public.flats;

CREATE TABLE public.flats (
    id int8 NULL,
    floor int8 NULL,
    is_apartment bool NULL,
    kitchen_area float8 NULL,
    living_area float8 NULL,
    rooms int8 NULL,
    studio bool NULL,
    total_area float8 NULL,
    price int8 NULL,
    building_id int8 NULL
);
CREATE INDEX ix_flats_id ON public.flats USING btree (id);

-- COPY public.flats(id, floor, is_apartment, kitchen_area, living_area, rooms, studio, total_area, price, building_id) FROM 'sp_1_project_flats_202402291420.csv' WITH (FORMAT csv, HEADER true);
