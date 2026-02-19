# CityJSON Extensions registry

This is the official registry for [CityJSON](https://www.cityjson.org/) Extensions. It provides a centralized location where developers can discover, submit, and maintain CityJSON Extensions that extend the core CityJSON specification.

## Overview

CityJSON Extensions allow you to add custom properties and objects to CityJSON datasets without modifying the core specification. This registry serves three key purposes:

- **Discoverability**: Software and developers can easily find and use existing Extensions
- **Reliability**: All Extensions are hosted in one location, eliminating CORS issues and broken links
- **Learning**: The community can learn from and build upon existing Extension implementations

## Available Extensions

<!-- EXTENSIONS_TABLE_START -->
| Extension | Description | Latest version | Schema | Developer(s) |
|-----------|-------------|----------------|--------|--------------|
| [energy-space-heating](https://github.com/cityjson/extensions/tree/main/extensions/energy-space-heating/1.1.1) | CityJSON Energy Extension for Space Heating Demand Calculation | 1.1.1 | [energy-space-heating.ext.json](https://cityjson.github.io/extensions/energy-space-heating/1.1.1/energy-space-heating.ext.json) | Özge Tufan |
| [perception](https://github.com/cityjson/extensions/tree/main/extensions/perception/0.5) | To model the visual perception of buildings | 0.5 | [perception.ext.json](https://cityjson.github.io/extensions/perception/0.5/perception.ext.json) | [Binyu Lei](https://binyulei.github.io/) |
| [quality](https://github.com/cityjson/extensions/tree/main/extensions/quality/1.0.1) | Application Domain Extension to data quality modeling | 1.0.1 | [quality.ext.json](https://cityjson.github.io/extensions/quality/1.0.1/quality.ext.json) | Grigory Ilizirov, Sagi Dalyot |
| [shed](https://github.com/cityjson/extensions/tree/main/extensions/shed/0.1.1) | Example of an Extension for modelling sheds; meant as a template to learn how to construct an Extension | 0.1.1 | [shed.ext.json](https://cityjson.github.io/extensions/shed/0.1.1/shed.ext.json) | [Hugo Ledoux](@hugoledoux) |
<!-- EXTENSIONS_TABLE_END -->


## Getting Started

### Using an Extension

To use a CityJSON Extension in your project:

1. Identify the Extension you need from the registry
2. Reference the Extension schema in your CityJSON file
3. Follow the Extension's documentation and examples

The URL to use is `https://cityjson.github.io/extensions/{name}/{version}/{name}.ext.json`.
Example reference in a CityJSON file:
```json
{
  "type": "CityJSON",
  "version": "2.0",
  "extensions": {
    "Lamppost": {
      "name": "https://cityjson.github.io/extensions/lamppost/0.1.0/lamppost.ext.json",
      "version": "0.1.0"
    }
  }
}
```

### Creating your own Extension

To create a new CityJSON Extension, refer to the [CityJSON Extension page](https://www.cityjson.org/extensions/#how-to-create-an-extension).

## Guidelines for submitting a new Extension

Before submitting, please ensure your Extension meets these criteria:

- **Usefulness**: The Extension should be useful to others and address a real need
- **Novelty**: Verify that no existing Extension already covers your use case
- **Naming**: 
  - Must be unique across the registry
  - Lowercase only, no spaces or capitals
  - Use hyphens to separate multiple words (e.g., `park-benches`, `solar-panels`)
- **Documentation**: Include both the Extension schema file and at least one example file demonstrating its usage
- **Licensing**: Add a license file to your package so others can use your work. We recommend [MIT](https://choosealicense.com/licenses/mit/) or [Apache 2.0](https://choosealicense.com/licenses/apache-2.0/). Not sure which? See [choosealicense.com](https://choosealicense.com)
- **Quality**: Code should be clear, well-documented, and follow best practices


## Directory Structure

Each Extension follows this structure within the registry:

```
extensions/
├── shed/
│   └── 0.1.0/
│       └── ...
│   └── 0.1.1/
│       ├── examples/
│       │   └── shed_example.json
│       ├── README.md
│       ├── shed.ext.json          <-- (Extension schema)
│       ├── extension.toml         <-- (metadata)
│       └── LICENSE.txt
├── energy/
│   └── 1.0.0/
│       ├── examples/
│       ├── README.md
│       ├── energy.ext.json
│       ├── extension.toml
│       └── LICENSE.txt
└── ...
```

### File Descriptions

- **`{name}.ext.json`**: The [CityJSON Extension schema file](https://www.cityjson.org/specs/#the-extension-file) containing the core definition
- **`extension.toml`**: Metadata about the Extension (name, version, author, etc.)
- **`README.md`**: Documentation explaining the Extension, its use cases, and examples 
- **`examples/`**: Directory containing example CityJSON files using this Extension
- **`LICENSE.txt`**: License file (MIT, Apache 2.0, or other)

## How to Submit an Extension

Once your Extension meets all the submission requirements above, follow these steps:

1. **Fork the repository** on GitHub

2. **Create the Extension directory structure**:
   ```
   git clone your-fork
   cd extensions
   mkdir -p extensions/{name}/{version}
   ```

3. **Add your Extension files**:
   - `{name}.ext.json` - Your Extension schema
   - `extension.toml` - Metadata file
   - `README.md` - Extension documentation
   - `examples/` - Folder with example CityJSON files
   - `LICENSE.txt` - License file

4. **Ensure the correct URL format**: Your Extension will be accessible at:
   ```
   https://cityjson.github.io/extensions/{name}/{version}/{name}.ext.json
   ```

5. **Commit and push** your changes to your fork

6. **Create a pull request** to the main repository with a clear description of your Extension

### Extension Schema Template

Here's a minimal example for a Lamppost Extension:

```json
{
  "type": "CityJSONExtension",
  "name": "Lamppost",
  "uri": "https://cityjson.github.io/extensions/lamppost/0.1.0/lamppost.ext.json",
  "version": "0.1.0",
  "versionCityJSON": "2.0",
  "description": "Extension to model Lampposts and street lighting infrastructure.",
  "extraRootProperties": {},
  "extraAttributes": {},
  "extraSemanticSurfaces": {},
  "extraCityObjects": {
    "Lamppost": {
      "description": "A single lamppost object",
      "properties": {...}
    }
  }
}
```


## Maintenance & Updates

- **Versioning**: Extensions follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- **Backward Compatibility**: Try to maintain backward compatibility when updating Extensions
- **Version Updates**: Submit new versions as separate directories (e.g., `lamppost/0.2.0/`)
- **Deprecation**: If an Extension is deprecated, clearly mark it in the README and documentation

## Resources

- [CityJSON Official Website](https://www.cityjson.org/)
- [CityJSON Specification](https://github.com/cityjson/spec)
- [CityJSON Extension Specification](https://www.cityjson.org/extensions/)
- [Semantic Versioning](https://semver.org/)
- [Choose a License](https://choosealicense.com)

## Community

We welcome contributions from the community! If you have questions or suggestions:

- **Open an Issue**: For bugs, questions, or feature requests
- **Start a Discussion**: For broader topics or design questions
- **Submit a Pull Request**: To add a new Extension or improve existing ones

## License

The registry itself is maintained by the CityJSON community. Each Extension in the registry is licensed according to its own LICENSE file.
