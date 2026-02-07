# EVE Model Gallery

A web-based 3D model viewer for EVE Online ships and structures, featuring an interactive gallery with multi-language support and advanced categorization.

![EVE Model Gallery](docs/Shiptree.png)

## 🚀 Features

- **Interactive 3D Model Viewer**: View EVE Online ship models in your browser using model-viewer
- **Multi-Language Support**: Fully localized in English and Chinese (中文)
- **Smart Categorization**: Models organized by category, group, and type from EVE's Static Data Export (SDE)
- **T3 Cruiser Variants**: Special support for Strategic Cruiser subsystem configurations with variant display
- **Icon Integration**: Automatic icon extraction and display from EVE's game assets
- **Model Deduplication**: Intelligent hash-based file management to optimize storage
- **Search Functionality**: Quick search across all ship types and categories
- **Responsive Design**: Glass-morphism UI with theme toggling and mobile-friendly layout

## 📋 Requirements

- Python 3.8 or higher
- Modern web browser with WebGL support
- EVE Online Static Data Export (SDE) files
- Icon assets from EVE Online

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlleyKatPr0/EVE_Model_Gallery.git
   cd EVE_Model_Gallery
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download and prepare SDE data**
   - Place `sde.zip` (containing the EVE SDE database files) in the `sde/` directory
   - Place `icons.zip` (containing EVE game icons) in the `sde/` directory

4. **Add 3D models**
   - Place ship model files (`.glb` or `.gltf` format) in the `docs/models/` directory
   - Model files should be named with the pattern: `{type_id}_{name}_*.glb`
   - For additional models not in the main SDE, use `docs/extra_models/` directory

5. **Initialize the data**
   ```bash
   python init.py
   ```
   
   This script will:
   - Extract SDE database and icon files
   - Scan and index all model files
   - Build categorized navigation trees
   - Generate JSON index files for both languages
   - Extract required icons to the statics directory
   - Deduplicate models based on file hashes

## 📖 Usage

### Running the Viewer

After initialization, open `docs/index.html` in a modern web browser. You can also serve it using a local web server:

```bash
# Using Python's built-in server
cd docs
python -m http.server 8000
```

Then navigate to `http://localhost:8000` in your browser.

### File Naming Convention

Model files should follow this naming pattern:
- Standard ships: `{type_id}_{ship_name}_suffix.glb`
- T3 Cruisers with variants: `{type_id}_{ship_name}{variant_code}_suffix.glb`
  - Example: `29984_Tengu2312_caldaribase_lite.glb` (variant code: 2312)

## 📁 Project Structure

```
EVE_Model_Gallery/
├── init.py                 # Data initialization script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore patterns
├── sde/                   # EVE Static Data Export files (not committed)
│   ├── sde.zip           # SDE database archive
│   └── icons.zip         # Icon assets archive
└── docs/                  # Web application root
    ├── index.html         # Main viewer page
    ├── css/               # Stylesheets
    ├── js/                # JavaScript files
    ├── models/            # Ship 3D model files (.glb/.gltf)
    ├── extra_models/      # Additional model files
    ├── statics/           # Generated static resources
    │   ├── icons/         # Extracted game icons
    │   ├── resources_index_en.json  # English index
    │   ├── resources_index_cn.json  # Chinese index
    │   └── available_models.json    # List of available models
    ├── Shiptree.png       # Project logo
    └── type_default.png   # Default type icon
```

## 🔧 Configuration

The `init.py` script can be customized by modifying the `EVEDataInitializer` class:
- Change output paths
- Modify category/group filters (currently set to categoryID 6 and 65 for ships)
- Adjust icon extraction logic
- Customize the tree building algorithm

## 🎨 Blender Integration

This project is based on **Blender 5.0**. If you want to bake or edit the models yourself, you can access the source Blender projects:

[Dropbox - Blender Projects](https://www.dropbox.com/scl/fo/erlilx1z22cha2le712yi/AO8Tmpg0vxFoReBkYoMGIns?rlkey=4nrbqup4lyfhr2t9mvqevi54p&st=o5rgi9y5&dl=0)

## 🙏 Credits & References

This project is based on the excellent work by **Ondřej Janíček**:
- [Release_EVE_Online_Ship_shader_.rar](https://onedrive.live.com/?id=5F4AD5A3DD3EC4D9%217994&cid=5F4AD5A3DD3EC4D9&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3UvYy81ZjRhZDVhM2RkM2VjNGQ5L0VkbkVQdDJqMVVvZ2dGODZId0FBQUFBQmVJaldxdXhhSGZEV0NSNnNfazg0c1E%5FZT1pUXVEZ3Y&parId=5F4AD5A3DD3EC4D9%21se3d4ac861dac4443b1dca5ae0625e466&o=OneUp)

**Special thanks to:**
- The **EVE Creative** community for all the help and shared resources
- CCP Games for EVE Online and the Static Data Export
- The model-viewer team for the excellent 3D viewer component

## 📱 Related Projects

**Tritanium** - EVE Online companion app for iOS:
- [App Store Link](https://apps.apple.com/us/app/tritanium/id6739530875)

## 📄 License

This project uses assets and data from EVE Online, which are owned by CCP Games. Please refer to [CCP's Developer License Agreement](https://developers.eveonline.com/resource/license-agreement) for usage terms.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📮 Support

For questions, issues, or suggestions, please open an issue on GitHub or contact the maintainer.
