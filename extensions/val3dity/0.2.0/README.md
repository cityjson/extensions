# Val3dity extension

The Val3dity extension stores validation results produced by [val3dity](https://github.com/tudelft3d/val3dity) in a CityJSON document. It is intended for workflows where validation diagnostics need to travel with the geometry, including per-geometry errors and the face or primitive reported by val3dity.

You can visually inspect the val3dity errors in CityJSON files that use this extensions with [CJLoupe](https://github.com/3DGI/CJLoupe).

## Root report

The root property `+val3dity-report` stores metadata about the validation run:

- `val3dityVersion`: version of val3dity used.
- `validity`: overall dataset validity.
- `parameters`: validation tolerances and other run parameters.
- `featuresOverview`, `primitivesOverview`, `errorCodeSummary`, and `datasetErrors`: dataset-level summaries.

## CityObject validation

The attribute `+val3dity-validation` can be added to any CityObject. Invalid geometries should include grouped errors under `geometries`; valid CityObjects may omit the attribute to keep files compact.

Each geometry validation record uses `geometryIndex` to refer to the existing CityObject `geometry` array. Geometry type and LoD are not duplicated because they are already stored on the referenced geometry.

Each error stores:

- `code`: val3dity numeric error code.
- `description`: val3dity error name.
- `info`: optional message from val3dity.
- `sourceId`: the original val3dity location string.
- `location`: a structured version of the location.

For val3dity ids such as `coid=0363100012164938-0|geom=0|shell=0|face=313`, the error is grouped under geometry record `geometryIndex=0`, and its structured location is relative to that geometry:

```json
{
  "shellIndex": 0,
  "faceIndex": 313
}
```

If a producer reports or derives a point location, `location.point` may be added with coordinates in the CityJSON dataset CRS after applying the CityJSON transform.

## Example

See `examples/val3dity_sample.json` for an example CityJSON file with embedded val3dity report based on val3dity's own [data/cityjsonseq/3dbag_b2.city.jsonl](https://github.com/tudelft3d/val3dity/blob/40d65ff7710e45a4bf64771c5ce9083243ccbf76/data/cityjsonseq/3dbag_b2.city.jsonl) test file.

## Merge utility

This repository includes `python/merge_val3dity_report.py` to merge a val3dity report into an existing CityJSON or CityJSONSeq file:

```sh
python3 python/merge_val3dity_report.py report.val3dity.json input.city.json output.city.json
```

For CityJSONSeq input, the output remains newline-delimited CityJSONSeq. By default, the utility writes validation attributes only for invalid geometries; use `--include-valid` to also add `validity=true` attributes for valid val3dity features.
