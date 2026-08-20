# CityJSON Dynamizer Extension

CityJSON Extension 2.0.0 for representing concepts from the [CityGML 3.0 Dynamizer module](https://docs.ogc.org/is/20-010/20-010.html#dynamizer-uml) in CityJSON 2.0.

The extension provides an encoding for time-varying CityObject properties, embedded and file-based time series, composite time series, and live or remote sensor connections.

- **Extension version:** 2.0.0
- **Target CityJSON version:** 2.0
- **Schema baseline used for testing:** CityJSON 2.0.2

## Version and relationship to earlier work

This extension builds on an [earlier Dynamizer extension proposal for CityJSON 1.1](https://github.com/1khawla/CityJSON-Dynamizer).

Version 2.0.0 introduces a redesigned encoding for CityJSON 2.0. Dynamizers and concrete time series are represented as identifiable CityObjects, the relation to the affected CityObject is explicitly represented through `target`, and the temporal and file-based encodings have been revised.

## Core representation

- `+Dynamizer` is an independent extension CityObject.
- `target` identifies the CityObject whose property changes.
- `attributeRef` is an RFC 6901 JSON Pointer evaluated relative to that target.
- `dynamicData` identifies a concrete time-series CityObject.
- Concrete series are `+GenericTimeseries`, `+CompositeTimeseries`, `+StandardFileTimeseries`, and `+TabulatedFileTimeseries`.
- `SensorConnection`, `TimeValuePair`, and `TimeseriesComponent` are embedded records because they do not need independent identities.
- The target-side `+dynamizer` attribute is an optional inverse reference provided for convenience. The `target` member remains the main relation from the Dynamizer to the affected CityObject.

```json
"dyn-temperature": {
  "type": "+Dynamizer",
  "attributes": {
    "target": "building-01",
    "attributeRef": "/attributes/temperature",
    "dynamicData": "series-temperature"
  }
}
```

## Supported concepts

| CityGML concept | CityJSON encoding |
| --- | --- |
| Dynamizer | `+Dynamizer` CityObject |
| GenericTimeseries | `+GenericTimeseries` CityObject |
| CompositeTimeseries | `+CompositeTimeseries` CityObject |
| StandardFileTimeseries | `+StandardFileTimeseries` CityObject |
| TabulatedFileTimeseries | `+TabulatedFileTimeseries` CityObject |
| SensorConnection | Embedded in `+Dynamizer` |
| TimeValuePair | Embedded typed record |
| TimeseriesComponent | Embedded reference record |
| Scalar values | Typed representations for `int`, `double`, `string`, `uri`, and `bool` |

Geometry-, implicit-geometry-, and appearance-valued Dynamizers are not included in version 2.0.0. Their CityGML meaning and the related CityJSON encoding difficulties are documented in the complete mapping specification, but no stable CityJSON encoding is currently proposed for them.

## Examples

The [`examples`](examples/) directory contains five CityJSON datasets based on the same TUM LoD2 building. They target `/attributes/temperature` while demonstrating different sources and organisations of temporal values.

| Example | Representation | Values are stored |
| --- | --- | --- |
| [`01-generic-embedded-time-value-pairs.city.json`](examples/01-generic-embedded-time-value-pairs.city.json) | Generic series | In embedded typed pairs |
| [`02-tabulated-file-timeseries.city.json`](examples/02-tabulated-file-timeseries.city.json) | Tabulated-file series | In [`data/temperature.csv`](data/temperature.csv) |
| [`03-standard-file-timeseries.city.json`](examples/03-standard-file-timeseries.city.json) | Standard-file series | In [`data/temperature-timeseriesml.xml`](data/temperature-timeseriesml.xml) |
| [`04-composite-timeseries.city.json`](examples/04-composite-timeseries.city.json) | Composite series | In referenced component series |
| [`05-sensor-connection.city.json`](examples/05-sensor-connection.city.json) | Sensor connection | Remotely in TUM FROST |

## Using the extension

Declare the extension in a CityJSON document as follows:

```json
"extensions": {
  "dynamizer": {
    "url": "https://cityjson.github.io/extensions/dynamizer/2.0.0/dynamizer.ext.json",
    "version": "2.0.0"
  }
}
```

## Validation

Install [`cjval`](https://github.com/cityjson/cjval), then run the following commands from this version directory:

```bash
cjvalext dynamizer.ext.json
cjval examples/01-generic-embedded-time-value-pairs.city.json -e dynamizer.ext.json
cjval examples/02-tabulated-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/03-standard-file-timeseries.city.json -e dynamizer.ext.json
cjval examples/04-composite-timeseries.city.json -e dynamizer.ext.json
cjval examples/05-sensor-connection.city.json -e dynamizer.ext.json
```

`cjval` checks CityJSON structure and conformance with the extension schema. Successful schema validation does not by itself prove that referenced IDs and JSON Pointers resolve, external resources and services are available, units are compatible, or a composite time-series graph is meaningful. These aspects require additional semantic or operational checks.

## Complete documentation and development repository

The complete mapping specification, generation scripts, reference-validation tool, and development history are available in the [CityJSON Dynamizer Extension development repository](https://github.com/JEDDOUB/cityjson-dynamizer-extension).

The mapping specification explains:

- the mapping of the supported CityGML Dynamizer concepts;
- the reasons behind the selected CityJSON representations;
- temporal values and JSON Pointer target addressing;
- units, code values, file-based series, and sensor connections;
- validation boundaries, known limitations, and possible future developments.

## Contact

This extension is developed by [Imane Jeddoub](https://github.com/JEDDOUB) within [GeoScITY](https://www.geoscity.uliege.be/), University of Liège.

Questions, suggestions, and feedback can be submitted through the development repository's [GitHub Issues](https://github.com/JEDDOUB/cityjson-dynamizer-extension/issues).

## References

- [OGC CityGML 3.0 Part 1: Conceptual Model](https://docs.ogc.org/is/20-010/20-010.html)
- [OGC CityGML 3.0 Part 2: GML Encoding](https://docs.ogc.org/is/21-006r2/21-006r2.html)
- [CityJSON 2.0.2 specification](https://www.cityjson.org/specs/2.0.2/)
- [CityJSON Extension mechanism](https://www.cityjson.org/specs/2.0.2/#extensions)
- [RFC 6901: JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901)
- [RFC 3339: Date and Time on the Internet](https://www.rfc-editor.org/rfc/rfc3339)

## Licence

This extension is licensed under the MIT License. See [`LICENSE.txt`](LICENSE.txt).
