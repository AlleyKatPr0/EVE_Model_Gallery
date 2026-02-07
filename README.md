# EVE Model Gallery

**A web-based 3D model viewer for EVE Online spaceships**

This repository contains an interactive 3D model gallery that displays EVE Online ship models directly in your web browser. Built with modern web technologies, it provides an immersive viewing experience for hundreds of EVE Online vessels.

## 🚀 Features

- **3D Model Viewing**: Interactive 3D rendering of EVE Online ships using glTF/GLB format
- **Camera Controls**: Rotate, zoom, and pan around models
- **Auto-Rotate**: Automatic model rotation for 360° viewing
- **Adjustable Lighting**: Brightness and shadow controls
- **Search & Browse**: Navigate through categorized ship collections
- **Theme Support**: Dark and light mode options
- **Mobile Responsive**: Works on desktop and mobile browsers

## 🌐 Live Demo

Visit the live site: [https://alleykatpr0.github.io/EVE_Model_Gallery/](https://alleykatpr0.github.io/EVE_Model_Gallery/)

## 🎮 Usage

Simply open `docs/index.html` in a modern web browser, or serve the `docs/` directory with any web server:

```bash
# Using Python
cd docs
python -m http.server 8000

# Then open http://localhost:8000 in your browser
```

## 🛠️ Technical Details

- **3D Rendering**: Google's `model-viewer` web component (v4.0.0)
- **Model Format**: glTF Binary (.glb)
- **Source**: Models based on Blender 5.0 exports
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## 📁 Project Structure

```
docs/
├── index.html          # Main viewer interface
├── models/             # Ship 3D models (.glb files)
├── extra_models/       # Additional models
├── js/                 # JavaScript application logic
├── css/                # Styling
└── statics/            # Icons and data indexes

init.py                 # Data initialization script
```

## 🎨 Model Editing

If you want to bake/edit the models yourself, check out the source projects: 

[Dropbox Project Files](https://www.dropbox.com/scl/fo/erlilx1z22cha2le712yi/AO8Tmpg0vxFoReBkYoMGIns?rlkey=4nrbqup4lyfhr2t9mvqevi54p&st=o5rgi9y5&dl=0)

## 📚 Reference

This project is based on: [Release_EVE_Online_Ship_shader_.rar](https://onedrive.live.com/?id=5F4AD5A3DD3EC4D9%217994&cid=5F4AD5A3DD3EC4D9&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3UvYy81ZjRhZDVhM2RkM2VjNGQ5L0VkbkVQdDJqMVVvZ2dGODZId0FBQUFBQmVJaldxdXhhSGZEV0NSNnNfazg0c1E%5FZT1pUXVEZ3Y&parId=5F4AD5A3DD3EC4D9%21se3d4ac861dac4443b1dca5ae0625e466&o=OneUp) from *Ondřej Janíček*.

Huge thanks to the *EVE Creative* community for all the help and shared resources.

## 🔗 Related Projects

**iOS App**: [Tritanium - EVE Online Tool](https://apps.apple.com/us/app/tritanium/id6739530875)

## ⚖️ License & Copyright

Model files and textures are property of CCP Games. This viewer is for non-commercial, educational purposes only.

## 🌟 Acknowledgments

- CCP Games for EVE Online
- Ondřej Janíček for shader work
- EVE Creative community
