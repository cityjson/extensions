# val3dity extension

The val3dity extension stores validation results produced by [val3dity](https://github.com/tudelft3d/val3dity) in a CityJSON document. 
It is intended for workflows where validation diagnostics need to travel with the geometry, including per-geometry errors and the face or primitive reported by val3dity.

You can visually inspect the val3dity errors in CityJSON files that use this extensions with [CJLoupe](https://github.com/3DGI/CJLoupe).

## Root report

The root property `+val3dity-report` stores metadata about the validation run:

- `val3dityVersion`: version of val3dity used.
- `validity`: overall dataset validity.
- `parameters`: validation tolerances and other run parameters.
- `featuresOverview`, `primitivesOverview`, `errorCodeSummary`, and `datasetErrors`: dataset-level summaries.

## CityObject validation

The attribute `+val3dity-validation` can be added to any CityObject. 
Invalid geometries should include grouped errors under `geometries`; valid CityObjects may omit the attribute to keep files compact.

Each geometry validation record uses `geometryIndex` to refer to the existing CityObject `geometry` array. 
Geometry type and LoD are not duplicated because they are already stored on the referenced geometry.

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

See folder `examples/` for 3 examples CityJSON files with embedded val3dity reports.


## val3dity integration

From v2.7.0 of val3dity, you can use the option `--report_in_cityjson` to directly embed the report in the input CityJSON file.
It adds the extension, the root property, and the report for each City Object.

It works for both CityJSON and CityJSONSeq files.
