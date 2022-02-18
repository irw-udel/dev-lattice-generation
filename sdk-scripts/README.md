Configuration of components

# Primitive

## Prepare

### Icon

`thought-balloon-twitter-1f4ad-24-stroke.png`

### Inputs

- primitive
    - Item access
    - Geometry base

### Compiling

- Nickname: ltprim
- Category: LatticeTools-Internal
- Subcategory: Primitive
- GUID: c1ae1e01-2f82-4b0e-ba3f-5e52d5eea33c

# Populate

## Lattice

Icon: `globe-with-meridians-twitter-1f310-24-stroke-scaled.png`

### Inputs

- core_voxels
    - List access
    - No type hint
- boundary_voxels
    - List access
    - No type hint
- unit_cell
    - List access
    - Curve
- connectivity
    - Item access
    - No type hint
- primitive
    - Item access
    - No type hint

### Compiling

- Nickname: ltpoplattice
- Category: LatticeTools-Internal
- Subcategory: Populate
- GUID: 47549020-43e6-4d88-8a56-0f41b2d5633e

# Mesh

## Meshing

Icon: `checkered-flag-twitter-1f3c1-24-stroke.png`

### Inputs

- run
    - Item access
    - bool
- curves
    - List access
    - Curve
- radius
    - List access
    - No type hint
- dendroSettings
    - Item access
    - No type hint
- surfaces
    - List access
    - Surface
- bake
    - Item access
    - bool
- save
    - Item access
    - bool
- file_name
    - Item access
    - str
- delete
    - Item access
    - bool

### Compiling

- Nickname: ltmesh
- Category: LatticeTools-Internal
- Subcategory: Mesh
- GUID: 0b2c3cca-1e24-4db7-9986-56faf7bd3b0e

# Logging

## System Info

Icon: `desktop-twitter-1f5a5-24-stroke.png`

### Inputs

- refresh
    - List access
    - No type hint
- project_dir
    - Item access
    - str
- save_directory
    - Item access
    - No type hint
- id_properties
    - List access
    - No type hint

### Compiling

- Nickname: ltcomp
- Category: LatticeTools-Internal
- Subcategory: Logging
- GUID: 5ec31517-e312-4797-9356-5bae05bd556c

## Logger

Icon: `memo-twitter-1f4dd-24-stroke.png`

### Inputs

- file_path
    - Item access
    - No type hint
- content
    - List access
    - str
- write_file
    - Item access
    - bool

### Compiling

- Nickname: ltlogger
- Category: LatticeTools-Internal
- Subcategory: Logging
- GUID: 7e18ab63-5677-41ca-b1a1-24ec39061284

## Combine JSON

Icon: `linked-paperclips-twitter-1f587-24-stroke.png`

### Inputs

- input_json
    - List access
    - str

### Compiling

- Nickname: ltjson
- Category: LatticeTools-Internal
- Subcategory: Logging
- GUID: 8d0669c4-4604-4b8d-9335-20db5e774f6c