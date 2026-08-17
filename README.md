# metal2f0

**metal2f0** converts BaseColor and Metallic textures into separate Diffuse / Albedo and F0 / Specular textures. This allows you to convert all existing textures from the Metallic Roughness workflow into [UE Substrate](https://dev.epicgames.com/documentation/unreal-engine/overview-of-substrate-materials-in-unreal-engine)-compatible variants. [Substrate](https://dev.epicgames.com/documentation/unreal-engine/overview-of-substrate-materials-in-unreal-engine) is the default material system since UE 5.7.

It supports both single-material conversion and batch conversion for larger texture collections.

## Features

* Convert BaseColor + Metalness into:
  * Diffuse / Albedo
  * F0 / Specular
* Support for RGB and RGBA images
* PNG, TGA and EXR image formats
* Configurable Metalness channel (Packed Textures)
* Configurable Specularity value
* Single-material conversion mode
* Batch conversion using filename patterns
  * Configurable output postfixes
  * Optional overwrite protection

## Usage

### Single Material

The **Single** tab is intended for individual conversions.

Provide:

* BaseColor texture
* Metalness texture
* Metalness channel
* Specularity value
* Output paths for Diffuse / Albedo and F0 / Specular

The default Specularity value is `0.04`, which is a common value for non-metallic materials.

The generated textures retain the dimensions and channel count of the BaseColor texture.

### Batch Conversion

The **Batch** tab is intended for converting larger sets of materials.

Instead of selecting individual files, specify:

* A base directory
* A BaseColor filename pattern
* A Metalness filename pattern
* Specularity
* Output postfixes
* Whether existing files may be overwritten

Patterns use exactly one `*` wildcard.

The wildcard represents the material key. For example:

```text
BaseColor: *_bc.png
Metalness:  *_orm.png
```

Given:

```text
Wood_A_bc.png
Wood_A_orm.png
Wood_B_bc.png
Wood_B_orm.png
```

the batch processor identifies two material pairs:

```text
Wood_A
Wood_B
```

Matching is case-sensitive.

Only postfix-style patterns are supported. Prefix patterns and multiple wildcards are intentionally not supported in order to keep the matching and output naming predictable.

## Development

The project uses [uv](https://docs.astral.sh/uv/) for Python environment and dependency management.

Install the project dependencies:

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest
```

The test suite covers:

* Image loading and saving
* PNG, TGA and EXR handling
* RGB and RGBA images
* Metal channel extraction
* Diffuse calculation
* F0 / Specular calculation
* Dimension validation
* Batch filename matching
* Batch processing
* Processor integration

## Building

The application is packaged with [PyInstaller](https://pyinstaller.org/).

The platform-specific executable name is defined in the PyInstaller spec:

* Windows: `metal2f0.exe`
* Linux: `metal2f0.x86_64`

Build locally with:

```bash
uv run pyinstaller packaging/metal2f0.spec
```

The resulting executable is placed in:

```text
dist/
```

## Project Structure

```text
metal2f0/
├── src/
│   └── metal2f0/
│       ├── processing/
│       │   ├── processor.py
│       │   └── batch.py
│       ├── ui/
│       ├── resources/
│       └── app.py
├── tests/
├── packaging/
│   └── metal2f0.spec
├── .github/
│   └── workflows/
│       └── build.yml
├── pyproject.toml
└── uv.lock
```

## License

metal2f0 is licensed under the MIT License. See [LICENSE](LICENSE) for the full license text.
