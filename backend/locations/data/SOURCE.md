# Source

`kenya_counties.json` is derived from the `counties.json` file in
[Mondieki/kenya-counties-subcounties](https://github.com/Mondieki/kenya-counties-subcounties)
(OpenStreetMap-derived boundary data, official KNBS/IEBC county codes 1-47).

Verified against public knowledge before use: county count (47), county codes
(Mombasa=1 ... Nairobi=47), and spot-checked sub-county lists for Nairobi,
Mombasa, Baringo, and Kajiado.

Cleaning applied: trimmed whitespace, removed trailing "Sub County"/"."
suffixes from sub-county names.

**Known gap:** Kisii County's sub-counties list was empty in the source data.
Rather than guess, only the county-level entry was imported for Kisii; its
sub-counties are missing until a verified list is added.

## Ward and town/area data

Not included. A ward-level dataset was checked
([alvinchesaro/Kenya-Counties-SubCounties-and-Wards](https://github.com/alvinchesaro/Kenya-Counties-SubCounties-and-Wards))
and found to be incorrect (e.g. it lists wards under Baringo County that
actually belong to Nyeri and Uasin Gishu counties), so it was not used.

To add wards: source a verified dataset (e.g. IEBC delimitation records or a
KNBS shapefile attribute table), add `Location` rows with
`level='ward'`/`'town'` and a `sub_county_name`/parent reference, then re-run
`python manage.py index_locations`.
