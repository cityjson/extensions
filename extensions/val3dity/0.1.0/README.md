# Val3dity extension

The Val3dity extension stores validation results produced by [val3dity](https://github.com/tudelft3d/val3dity) in a CityJSON document. It is intended for workflows where validation diagnostics need to travel with the geometry, including per-geometry errors and the face or primitive reported by val3dity.

## Root report

The root property `+val3dity-report` stores metadata about the validation run:

- `val3dityVersion`: version of val3dity used.
- `inputFile` and `inputFileType`: source reported by val3dity.
- `time`: validation run time as reported by val3dity.
- `validity`: overall dataset validity.
- `parameters`: validation tolerances and other run parameters.
- `featuresOverview`, `primitivesOverview`, `allErrors`, `errorCodeSummary`, and `datasetErrors`: dataset-level summaries.

## CityObject validation

The attribute `+val3dity-validation` can be added to any CityObject. Invalid geometries should include grouped errors under `geometries`; valid CityObjects may omit the attribute to keep files compact.

Each geometry validation record uses `geometryIndex` to refer to the existing CityObject `geometry` array. Geometry type and LoD are not duplicated because they are already stored on the referenced geometry.

Each error stores:

- `code`: val3dity numeric error code.
- `description`: val3dity error name.
- `info`: optional message from val3dity.
- `sourceId`: the original val3dity location string.
- `location`: a structured version of the location.

For val3dity ids such as `coid=0363100012164938-0|geom=0|shell=0|face=313`, the structured location is:

```json
{
  "cityObjectId": "0363100012164938-0",
  "geometryIndex": 0,
  "shellIndex": 0,
  "faceIndex": 313
}
```

If a producer reports or derives a point location, `location.point` may be added with coordinates in the CityJSON dataset CRS after applying the CityJSON transform.

## Example

See `examples/val3dity_sample.json` for a compact example based on a val3dity report for CityJSONSeq. The report feature is a `Building`, while val3dity points to the geometry-owning `BuildingPart`; the extension therefore stores the diagnostics on the `BuildingPart` and keeps the original report feature id in `reportFeatureId`.

## Merge utility

This repository includes `python/merge_val3dity_report.py` to merge a val3dity report into an existing CityJSON or CityJSONSeq file:

```sh
python3 python/merge_val3dity_report.py report.val3dity.json input.city.json output.city.json
```

For CityJSONSeq input, the output remains newline-delimited CityJSONSeq. By default, the utility writes validation attributes only for invalid geometries; use `--include-valid` to also add `validity=true` attributes for valid val3dity features.
