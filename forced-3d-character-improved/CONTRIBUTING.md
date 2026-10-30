# Contributing

Thanks for improving AI 3D Character Creator.

## Before submitting changes

1. Keep character-specific choices in JSON configuration files instead of hard-coding them into the generator.
2. Document Blender-version-specific API changes and export limitations.
3. Add or update tests for configuration and helper behavior.
4. Run these checks from the repository root:

   ```bash
   python -m compileall -q scripts tests
   python scripts/validate_config.py configs/default_character.json
   python scripts/validate_config.py examples/dark_suit_purple_eyes.json
   python -m unittest discover -s tests -v
   ```

5. When changing Blender geometry or exporters, run the documented generation and import-validation commands on a machine with Blender installed. Record the Blender version and results; Python-only checks do not prove a Blender render/export works.

## Scope

The current model is a procedural low-poly starter. Do not describe it as rigged, animation-ready, production topology, or visually validated unless those properties have actually been implemented and tested.
