# 🍌 Nano Banana Image Composition App

A powerful AI-powered image composition tool that uses Google's **Gemini 2.5 Flash Image Preview** model to seamlessly blend objects from one image into another with precise placement control.

![Nano Banana Demo](generated_composite.png)

## ✨ Features

- **🎯 Precise Object Placement**: Draw bounding boxes to specify exactly where objects should be placed
- **🤖 AI-Powered Composition**: Uses Google's cutting-edge Gemini 2.5 Flash Image Preview model
- **🖼️ Clean Output**: No visible editing marks, borders, or coordinate annotations
- **📁 PNG Export**: Automatic conversion to high-quality PNG format
- **💾 One-Click Download**: Easy download functionality for generated images
- **🔧 Advanced Debugging**: Comprehensive error handling and debug mode
- **📱 Web Interface**: User-friendly Gradio-powered web interface

## � Quick Start

### Prerequisites

- Python 3.8+
- Google API key for Gemini
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Marvel202/banana-app.git
   cd banana-app
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   
   Get your Google API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser** and navigate to the displayed URL (typically `http://localhost:7860`)

## 🎮 How to Use

### Simple Nano Banana Generation (`app.py`)
1. Enter a text prompt describing what you want to generate
2. Click "Generate Nano Banana Image"
3. Download your generated image

### Advanced Image Composition (`app2.py`)
1. **Upload Background Image**: Upload the image where you want to place an object
2. **Draw Bounding Box**: Click and drag to draw a rectangle where the object should be placed
3. **Upload Object Image**: Upload the image containing the object you want to insert
4. **Generate**: Click "Generate Composite Image"
5. **Download**: Use the download button to save your PNG result

## 📁 Project Structure

```
banana-app/
├── app.py                      # Simple nano banana generator
├── app2.py                     # Advanced image composition tool
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── examples/                   # Example images for testing
├── venv/                       # Virtual environment (create this)
└── generated_composite.png     # Sample output
```

## 🛠️ Technical Details

### Core Technologies
- **Google Gemini 2.5 Flash Image Preview**: State-of-the-art AI image generation
- **Gradio**: Modern web interface framework
- **PIL/Pillow**: Image processing and format conversion
- **gradio_image_annotation**: Interactive bounding box drawing

### Key Features
- **Format Detection**: Automatically detects Gemini's output format (typically WebP)
- **PNG Conversion**: Forces conversion to PNG with proper color handling
- **Bounding Box Removal**: Intelligent prompting to avoid visible editing marks
- **Error Handling**: Comprehensive debugging and error recovery
- **File Management**: Automatic cleanup of temporary files

## 🎨 Examples

The app includes several example image pairs in the `examples/` directory:
- Portrait composition examples
- Object insertion scenarios
- Various aspect ratios and image types

## 🔧 Configuration

### Debug Mode
Enable debug mode in the interface to see detailed processing information:
- API call details
- Image format detection
- Processing steps
- Error diagnostics

### Environment Variables
- `GOOGLE_API_KEY`: Your Google API key (required)

## 📋 Requirements

See `requirements.txt` for complete dependency list:
- `gradio>=4.0.0`
- `google-genai`
- `Pillow>=9.0.0`
- `numpy`
- `python-dotenv`
- `gradio_image_annotation`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI** for the incredible Gemini 2.5 Flash Image Preview model
- **Gradio team** for the excellent web interface framework
- **Community contributors** for testing and feedback

## 🐛 Troubleshooting

### Common Issues

1. **"No Google API key found"**
   - Ensure your `.env` file exists and contains `GOOGLE_API_KEY=your_key`
   - Verify your API key is valid and active

2. **"ModuleNotFoundError"**
   - Activate your virtual environment: `source venv/bin/activate`
   - Install requirements: `pip install -r requirements.txt`

3. **"Image not displaying"**
   - Check the console for detailed error messages
   - Enable debug mode for more information
   - Verify both images are uploaded correctly

4. **"Download button not working"**
   - Ensure an image has been generated first
   - Check if `generated_composite.png` exists in the project directory

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Enable debug mode for detailed information
3. Open an issue on GitHub with error details and steps to reproduce

## 🔗 Links

- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gradio Documentation](https://gradio.app/docs/)
- [Project Repository](https://github.com/Marvel202/banana-app)

---

**Made with 🍌 and AI magic**