# EVE Model Gallery - 3D Viewer Features

## Overview

Yes, **this repository absolutely displays 3D graphics in a web browser!** 

This is a fully-featured web-based 3D model viewer specifically designed for EVE Online spaceship models.

## How It Works

### Technology Stack

1. **3D Rendering Engine**: Google's `<model-viewer>` web component (v4.0.0)
   - Hardware-accelerated WebGL rendering
   - No plugins required - runs directly in modern browsers
   - Supports glTF 2.0 format (industry standard for 3D on the web)

2. **Model Format**: glTF Binary (.glb)
   - Optimized 3D format for web delivery
   - Includes meshes, materials, textures, and animations
   - Based on Blender 5.0 exports

3. **Frontend**: Pure web technologies
   - HTML5 for structure
   - CSS3 for styling and animations
   - Vanilla JavaScript for interactivity

## Interactive Features

### Viewer Controls
- **Auto-Rotate**: Automatic 360° rotation of models
- **Camera Controls**: 
  - Click and drag to rotate
  - Scroll to zoom in/out
  - Pan to move around the model
- **Brightness Slider**: Adjust exposure from 0.5x to 3.0x
- **Shadow Toggle**: Enable/disable dynamic shadows
- **Reset View**: Return to default camera position

### Navigation
- **Hierarchical Browser**: Ships organized by category and group
- **Search**: Find ships by name or ID
- **Breadcrumb Trail**: Track your location in the tree
- **Mobile Support**: Touch-friendly on smartphones and tablets

### Visual Options
- **Theme Toggle**: Switch between dark and light modes
- **Real-time Lighting**: Dynamic lighting and shadows
- **Material Rendering**: Accurate colors, metallicity, and roughness

## Model Library

The viewer includes hundreds of EVE Online ship models:

- **Categories**: Ships (Category 6) and Structures (Category 65)
- **Groups**: Frigates, Cruisers, Battleships, Capitals, etc.
- **Variants**: Special variants for T3 Cruisers (Group 963)

Each model includes:
- High-quality geometry (thousands to millions of polygons)
- PBR (Physically Based Rendering) materials
- Texture maps (color, metallic, roughness)
- Optimized for web performance

## Browser Compatibility

Works in all modern browsers that support:
- WebGL 2.0
- ES6 JavaScript
- Custom Elements v1

Tested on:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (Chrome, Safari)

## How to View

### Option 1: GitHub Pages (Live Demo)
Visit: https://alleykatpr0.github.io/EVE_Model_Gallery/

### Option 2: Local Viewing
```bash
cd docs
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

### Option 3: Direct File Opening
Simply open `docs/index.html` in a modern web browser
(Note: Some features may require a web server)

## Example Usage

1. **Open the viewer** in your web browser
2. **Browse or search** for a ship in the left sidebar
3. **Click a ship** to load its 3D model
4. **Interact** with the model:
   - Rotate by dragging
   - Zoom with scroll wheel
   - Adjust brightness with the slider
   - Toggle shadows for different looks
5. **Explore variants** (for T3 Cruisers) by clicking variant buttons

## Performance

The viewer is optimized for web performance:
- **Lazy Loading**: Models load on-demand
- **Compressed Format**: glTF Binary (.glb) for fast transfer
- **Progress Indicators**: Loading spinners and percentage
- **Error Handling**: Graceful fallbacks for missing models

## Conclusion

This repository is a **complete 3D graphics viewer** that runs entirely in your web browser. No installation, no plugins, no downloads required - just open the page and start exploring EVE Online ships in full 3D!
