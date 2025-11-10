# 🤖 Virtual Robot VR Teleoperation System

A real-time virtual robot teleoperation system using WebXR and WebRTC, enabling VR headset users to control and view through a simulated robot's stereo vision.

## ✨ Features

- **Stereo Vision Rendering**: Real-time dual-camera rendering from robot's perspective using PyBullet
- **WebRTC Streaming**: Low-latency video streaming with Side-by-Side or dual-track modes
- **VR Control**: Head tracking and controller input support via WebXR
- **Physics Simulation**: 240Hz physics simulation for realistic robot behavior
- **Flexible Configuration**: Adjustable resolution, framerate, and video modes

## 📋 System Architecture

```
VR Client (Browser) ←→ WebRTC ←→ Virtual Robot Server (Python + PyBullet)
     WebXR                           Physics Simulation
  Three.js                           Stereo Camera
                                     WebSocket Signaling
```

**Components:**
- **VR Client**: Three.js + WebXR running in VR headset browser
- **Virtual Robot**: PyBullet physics simulation + stereo camera rendering
- **Communication**: WebRTC for real-time video + WebSocket for signaling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- VR headset with WebXR support (Meta Quest, etc.)

### 1. Install Dependencies

**Virtual Robot Server (Python):**
```bash
cd virtual-robot
pip install -r requirements.txt
```

**VR Client (Node.js):**
```bash
cd ..
npm install
```

### 2. Generate SSL Certificate

WebXR requires HTTPS. Generate a self-signed certificate:

```bash
cd virtual-robot
python generate_cert.py
```

Or use the provided utility script that auto-generates certificates:
```bash
python -c "from generate_cert import generate_certificate; generate_certificate()"
```

### 3. Start Virtual Robot Server

```bash
python main.py
```

**Command Line Options:**
- `--gui`: Show PyBullet GUI (for debugging)
- `--fps 30`: Set video framerate (default: 30)
- `--width 640`: Set video width (default: 640)
- `--height 480`: Set video height (default: 480)
- `--no-ssl`: Disable SSL (use WS instead of WSS)
- `--test-pattern`: Use test pattern (red/blue for debugging stereo)
- `--video-mode sbs|dual`: Video mode (default: sbs)

**Examples:**
```bash
# High resolution, 60fps
python main.py --fps 60 --width 1280 --height 720

# Debug mode with GUI and test pattern
python main.py --gui --test-pattern

# Dual track mode (separate left/right streams)
python main.py --video-mode dual
```

### 4. Start VR Client

In a **separate terminal**:

```bash
npm run dev
```

### 5. Enter VR

1. Open VR headset browser and navigate to: `https://localhost:5173`
2. Accept the self-signed certificate warning
3. Wait for WebRTC connection to establish
4. Click "ENTER VR" button
5. Move your head and controllers to control the robot

## 📊 What to Expect

### In VR Headset
- Real-time stereo vision from robot's perspective
- Separate left/right eye views for depth perception
- Simulated environment with colored cubes and ground plane
- Smooth head tracking with robot camera following your movements

### Performance
- **Video**: 30-60 fps (configurable)
- **Physics**: 240 Hz simulation
- **Latency**: ~50-100ms (local network)
- **Resolution**: 640x480 to 1920x1080 per eye (configurable)

## 🛠️ Technology Stack

### Server Side (Python)
- **PyBullet** - Physics simulation and rendering engine
- **aiortc** - WebRTC implementation for Python
- **OpenCV** - Image processing and format conversion
- **websockets** - WebSocket server for signaling
- **asyncio** - Asynchronous I/O for concurrent operations

### Client Side (JavaScript)
- **Three.js** - 3D rendering engine
- **WebXR Device API** - VR headset interface
- **WebRTC API** - Real-time video streaming
- **Vite** - Development server and build tool

## 📁 Project Structure

```
virtual-robot/
├── main.py                 # Main entry point and server orchestration
├── robot_sim.py            # PyBullet robot simulation
├── stereo_camera.py        # Virtual stereo camera rendering
├── webrtc_server.py        # WebRTC server implementation
├── signaling_server.py     # WebSocket signaling server
├── generate_cert.py        # SSL certificate generation utility
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file

../ (VR Client - parent directory)
├── src/
│   ├── webrtc-client.js   # WebRTC client implementation
│   └── vr-scene.js        # VR scene and rendering
├── main.js                # Client entry point
├── index.html             # HTML page
└── package.json           # Node.js dependencies
```

## 🔧 Troubleshooting

### WebRTC Connection Issues

**Symptoms**: Client can't connect to server, connection timeout

**Solutions**:
1. Ensure server is running: `python main.py`
2. Check firewall allows port 8080
3. Verify SSL certificate is generated: `ls cert.pem key.pem`
4. Check browser console for detailed error messages
5. Try disabling SSL: `python main.py --no-ssl` (not recommended for production)

### No Video Stream

**Symptoms**: Connected but black screen in VR

**Solutions**:
1. Verify WebRTC connection state is "connected"
2. Try test pattern mode: `python main.py --test-pattern`
3. Lower resolution/framerate: `python main.py --fps 15 --width 320 --height 240`
4. Check browser WebRTC support (Chrome/Edge recommended)

### PyBullet Installation Issues

**Windows**:
```bash
pip install --upgrade pybullet
```

**Linux**:
```bash
sudo apt-get install python3-dev
pip install pybullet
```

**macOS**:
```bash
pip install pybullet
```

### aiortc Installation Issues

**Windows**:
- Install Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Then: `pip install aiortc`

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libavfilter-dev libopus-dev \
    libvpx-dev pkg-config
pip install aiortc
```

**macOS**:
```bash
brew install ffmpeg opus libvpx pkg-config
pip install aiortc
```

### Certificate Warnings

**Symptom**: Browser shows "Your connection is not private"

**Solution**: This is expected with self-signed certificates. Click "Advanced" → "Proceed to localhost" (or similar). For production, use a proper SSL certificate from Let's Encrypt or similar CA.

## 🎯 Roadmap

- [ ] Inverse kinematics for arm control via VR controllers
- [ ] Performance monitoring (FPS, latency, bandwidth)
- [ ] Support for custom robot models (URDF import)
- [ ] Object interaction and manipulation
- [ ] Multi-user support
- [ ] Recording and playback of teleoperation sessions
- [ ] Integration with real robot hardware
- [ ] Advanced physics interactions (grasping, force feedback)

## 🔬 Technical Details

### Video Modes

**Side-by-Side (SBS) Mode** (Default):
- Single video track with left/right images concatenated horizontally
- Resolution: `width*2 x height`
- Pros: Perfect synchronization, simpler client code
- Cons: Higher bandwidth per track

**Dual Track Mode**:
- Separate video tracks for left and right eyes
- Resolution: `width x height` per track
- Pros: Better compression, standard WebRTC approach
- Cons: Potential sync issues, track order uncertainty

### Camera Configuration

- **IPD (Interpupillary Distance)**: 64mm (configurable)
- **FOV (Field of View)**: 90° (configurable)
- **Near Plane**: 0.01m
- **Far Plane**: 100m

### Network Requirements

- **Bandwidth**: ~5-20 Mbps depending on resolution and FPS
- **Latency**: <100ms recommended for good experience
- **Protocol**: WebRTC (UDP-based) for video, WebSocket for signaling

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or issues, please open an issue on GitHub.

## 🙏 Acknowledgments

- PyBullet for physics simulation
- aiortc for Python WebRTC implementation
- Three.js for VR rendering
- WebXR community for standards and examples

