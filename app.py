import gradio as gr
from gradio_image_annotation import image_annotator
from google import genai
from google.genai import types
from PIL import Image
import io
import base64
import numpy as np
import os
import traceback
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug mode flag
DEBUG_MODE = True

def log_debug(message):
    """Debug logging function"""
    if DEBUG_MODE:
        print(f"🐛 DEBUG: {message}")

def process_images(annotated_image, second_image, debug_enabled=False, progress=gr.Progress()):
    """
    Process the annotated image and second image using Gemini's Nano Banana model
    """
    # IMMEDIATE DEBUG - This should always show in terminal
    print("🚀 URGENT DEBUG: Function process_images called!")
    print(f"🚀 annotated_image type: {type(annotated_image)}")
    print(f"🚀 second_image type: {type(second_image)}")
    print(f"🚀 debug_enabled: {debug_enabled}")
    
    # IMMEDIATE TEST - Return something to verify interface works
    if not annotated_image and not second_image:
        return None, "🚀 DEBUG: Function called but no images provided"
    
    log_debug("Function called - process_images")
    print("🚀 FUNCTION CALLED: process_images")
    
    debug_info = []
    debug_info.append("🚀 Function execution started")
    
    try:
        # Check if annotated_image is provided
        if annotated_image is None:
            error_msg = "Please provide the first image and draw an annotation box"
            debug_info.append(f"❌ {error_msg}")
            return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

        # Check if second_image is provided (could be None or numpy array)
        if second_image is None or (isinstance(second_image, np.ndarray) and second_image.size == 0):
            error_msg = "Please provide the second image"
            debug_info.append(f"❌ {error_msg}")
            return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

        # Check if annotation box exists
        if not annotated_image.get("boxes") or len(annotated_image["boxes"]) == 0:
            error_msg = "Please draw an annotation box on the first image"
            debug_info.append(f"❌ {error_msg}")
            return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

        # Extract bounding box coordinates
        box = annotated_image["boxes"][0]  # Get the first (and only) box
        xmin = box.get("xmin")
        ymin = box.get("ymin")
        xmax = box.get("xmax")
        ymax = box.get("ymax")
        
        debug_info.append(f"📐 Bounding box: ({xmin}, {ymin}) to ({xmax}, {ymax})")
        log_debug(f"Bounding box: ({xmin}, {ymin}) to ({xmax}, {ymax})")

        # Construct the dynamic prompt for Nano Banana model
        prompt = f"""You are an expert photo editor using nano banana technology. Please intelligently combine these two images:

        Task: Take the central object from the second image and seamlessly integrate it into the first image within the specified rectangular area.

        Placement coordinates: The object should be placed within the bounding box defined by:
        - Top-left corner: ({xmin}, {ymin})
        - Bottom-right corner: ({xmax}, {ymax})

        Requirements:
        1. Maintain realistic lighting and shadows that match the first image
        2. Ensure proper perspective and scaling of the inserted object
        3. Blend the object naturally with the background
        4. Preserve the style and aesthetic of the original first image
        5. Pay attention to color temperature and lighting consistency

        Create a photorealistic composite image that looks natural and professionally edited."""
        
        debug_info.append(f"📝 Generated prompt for Nano Banana")
        log_debug("Prompt generated for Nano Banana model")

        progress(0.2, desc="Preparing images for Gemini...")

        # Check API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            error_msg = "❌ No Google API key found in environment variables"
            debug_info.append(error_msg)
            return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

        debug_info.append(f"✅ Google API key found")
        log_debug("Google API key loaded")

        # Initialize Gemini client
        try:
            client = genai.Client(api_key=api_key)
            debug_info.append("✅ Gemini client initialized")
            log_debug("Gemini client initialized")
        except Exception as client_error:
            error_msg = f"Failed to initialize Gemini client: {str(client_error)}"
            debug_info.append(f"❌ {error_msg}")
            return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

        progress(0.4, desc="Processing first image...")

        # Process first image
        first_img = annotated_image["image"]
        if isinstance(first_img, np.ndarray):
            first_img_pil = Image.fromarray(first_img.astype('uint8'))
        else:
            first_img_pil = first_img

        # Save first image to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp1:
            first_img_pil.save(tmp1.name, format='PNG')
            first_img_path = tmp1.name
            debug_info.append(f"💾 First image saved: {first_img_path}")

        progress(0.5, desc="Processing second image...")

        # Process second image
        if isinstance(second_image, np.ndarray):
            second_img_pil = Image.fromarray(second_image.astype('uint8'))
        else:
            second_img_pil = second_image

        # Save second image to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp2:
            second_img_pil.save(tmp2.name, format='PNG')
            second_img_path = tmp2.name
            debug_info.append(f"💾 Second image saved: {second_img_path}")

        progress(0.7, desc="Sending to Nano Banana model...")

        # Enhanced prompt for image composition following the official documentation
        enhanced_prompt = f"""Create a seamless composite image by taking the central object from the second image and naturally integrating it into the first image within the specified rectangular area.

PLACEMENT COORDINATES (for internal use only): Place the object within bounding box coordinates:
- Top-left: ({xmin}, {ymin})  
- Bottom-right: ({xmax}, {ymax})

CRITICAL REQUIREMENTS:
- DO NOT draw, show, or display any bounding boxes, borders, rectangles, or coordinate markers on the final image
- DO NOT include any text, numbers, or coordinate labels on the image
- Create a clean, natural composite without any visible editing marks or annotations
- Maintain realistic lighting and shadows that match the first image
- Ensure proper perspective and scaling of the inserted object  
- Blend the object naturally with the background
- Preserve the style and aesthetic of the original first image
- Pay attention to color temperature and lighting consistency

OUTPUT FORMAT: Generate the result as a PNG image.

Create a photorealistic composite image that looks completely natural and professionally edited, with no visible signs of digital manipulation or coordinate markings."""

        debug_info.append(f"📝 Enhanced prompt created")
        log_debug("Enhanced prompt for image editing created")

        try:
            # Use the official format: [prompt, image1, image2] as shown in documentation
            print(f"🚀 SENDING TO GEMINI: prompt length = {len(enhanced_prompt)}")
            print(f"🖼️ IMAGE 1: {first_img_pil.size}, mode: {first_img_pil.mode}")
            print(f"🖼️ IMAGE 2: {second_img_pil.size}, mode: {second_img_pil.mode}")
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[enhanced_prompt, first_img_pil, second_img_pil],
            )
            
            debug_info.append("✅ Received response from Gemini")
            log_debug("Response received from Gemini")
            print(f"✅ RESPONSE RECEIVED!")

            # DETAILED RESPONSE DEBUGGING
            print(f"🔍 RESPONSE TYPE: {type(response)}")
            print(f"🔍 RESPONSE ATTRIBUTES: {dir(response)}")
            print(f"🔍 RESPONSE DEBUG: candidates count = {len(response.candidates) if response.candidates else 0}")
            debug_info.append(f"🔍 Response candidates count: {len(response.candidates) if response.candidates else 0}")

            progress(0.9, desc="Processing generated image...")

            # Process the response
            if not response.candidates or len(response.candidates) == 0:
                error_msg = "No response candidates received"
                debug_info.append(f"❌ {error_msg}")
                return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

            candidate = response.candidates[0]
            parts_count = len(candidate.content.parts)
            debug_info.append(f"📊 Processing candidate with {parts_count} parts")
            print(f"🔍 PARTS DEBUG: {parts_count} parts found")
            print(f"🔍 CANDIDATE TYPE: {type(candidate)}")
            print(f"🔍 CONTENT TYPE: {type(candidate.content)}")

            for i, part in enumerate(candidate.content.parts):
                has_text = part.text is not None
                has_inline_data = part.inline_data is not None
                debug_info.append(f"📋 Part {i}: text={has_text}, inline_data={has_inline_data}")
                print(f"🔍 PART {i} DEBUG: text={has_text}, inline_data={has_inline_data}")
                print(f"🔍 PART {i} TYPE: {type(part)}")
                print(f"🔍 PART {i} ATTRIBUTES: {dir(part)}")
                
                if has_text:
                    text_preview = part.text[:200] if part.text else "None"
                    debug_info.append(f"📄 Text response: {text_preview}...")
                    print(f"🔍 TEXT CONTENT: {text_preview}")
                    final_status = f"Gemini Response (Text Only): {part.text}"
                    if debug_enabled:
                        final_status += f"\n\nDebug Info:\n" + "\n".join(debug_info)
                    return None, final_status
                    
                elif has_inline_data:
                    print(f"🔍 INLINE_DATA TYPE: {type(part.inline_data)}")
                    print(f"🔍 INLINE_DATA ATTRIBUTES: {dir(part.inline_data)}")
                    print(f"🔍 DATA SIZE: {len(part.inline_data.data)} bytes")
                    
                    try:
                        # Convert the generated image data to PIL Image
                        image = Image.open(io.BytesIO(part.inline_data.data))
                        debug_info.append(f"✅ Image created: {image.size}, mode: {image.mode}")
                        print(f"✅ IMAGE CREATED: {image.size}, mode: {image.mode}")
                        
                        # Check what format Gemini actually returned
                        original_format = image.format if hasattr(image, 'format') else "Unknown"
                        print(f"🔍 ORIGINAL FORMAT FROM GEMINI: {original_format}")
                        debug_info.append(f"📋 Original format from Gemini: {original_format}")
                        
                        # Force convert to RGB for PNG compatibility
                        if image.mode in ('RGBA', 'P', 'LA'):
                            # Convert palette and LA to RGBA first, then to RGB
                            if image.mode in ('P', 'LA'):
                                image = image.convert('RGBA')
                            # Convert RGBA to RGB with white background to remove transparency
                            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                            if image.mode == 'RGBA':
                                rgb_image.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                            else:
                                rgb_image.paste(image)
                            image = rgb_image
                        elif image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        print(f"✅ CONVERTED TO: {image.mode}")
                        debug_info.append(f"✅ Converted to mode: {image.mode}")
                        
                        # Save the composite image with full path as PNG
                        output_dir = os.path.dirname(os.path.abspath(__file__))
                        composite_path = os.path.join(output_dir, "generated_composite.png")
                        
                        # Force save as PNG with high quality
                        image.save(composite_path, format='PNG', optimize=False, compress_level=1)
                        debug_info.append(f"💾 Composite image saved as PNG: {composite_path}")
                        print(f"💾 SAVED AS PNG TO: {composite_path}")
                        
                        # Verify the saved file format
                        saved_image = Image.open(composite_path)
                        print(f"🔍 SAVED FILE FORMAT: {saved_image.format}")
                        debug_info.append(f"🔍 Saved file format: {saved_image.format}")
                        
                        progress(1.0, desc="Composite image generated successfully!")
                        
                        final_status = f"✅ Clean composite image generated successfully!\n📁 Original format: {original_format} → Converted to PNG\n� Saved as: generated_composite.png\n📌 No bounding box markings included"
                        if debug_enabled:
                            final_status += f"\n\nDebug Info:\n" + "\n".join(debug_info[-8:])  # Show last 8 debug messages
                        
                        print(f"🎉 RETURNING CLEAN PNG IMAGE: {type(image)}")
                        return image, final_status
                        
                    except Exception as img_error:
                        error_msg = f"Failed to process generated image: {str(img_error)}"
                        debug_info.append(f"❌ {error_msg}")
                        return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

            error_msg = "No image was generated. Please try again."
            debug_info.append(f"❌ {error_msg}")
            return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

        except Exception as api_error:
            error_msg = f"Gemini API error: {str(api_error)}"
            debug_info.append(f"❌ {error_msg}")
            log_debug(error_msg)
            traceback.print_exc()
            return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg

        finally:
            # Clean up temp files
            try:
                if 'first_img_path' in locals():
                    os.unlink(first_img_path)
                if 'second_img_path' in locals():
                    os.unlink(second_img_path)
                debug_info.append("🧹 Temporary files cleaned up")
            except:
                pass

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        debug_info.append(f"❌ {error_msg}")
        log_debug(error_msg)
        traceback.print_exc()
        return None, f"{error_msg}\n\nDebug Info:\n" + "\n".join(debug_info) if debug_enabled else error_msg


def simple_interface_test():
    """Simple test to verify Gradio interface is working"""
    print("✅ SIMPLE TEST BUTTON CLICKED!")
    return None, "✅ Interface test successful! Button clicks are working."


def download_image():
    """Function to handle image download"""
    try:
        # Check if the generated image exists
        output_dir = os.path.dirname(os.path.abspath(__file__))
        composite_path = os.path.join(output_dir, "generated_composite.png")
        
        if os.path.exists(composite_path):
            # Return the file path for download
            return composite_path
        else:
            print("❌ No generated image found to download")
            return None
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None


# HTML banner for examples
examples_image_banner = gr.HTML(
        """
        <style>
            .animation-container {
                width: 100%;
                height: 400px;
                background: linear-gradient(135deg, #fff4e6 0%, #ffe8cc 25%, #ffeaa7 50%, #fdcb6e 75%, #ffecb3 100%);
                border-radius: 10px;
                margin-bottom: 20px;
                position: relative;
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .mini-container {
                position: relative;
                width: 600px;
                height: 300px;
                perspective: 1000px;
            }

            .mini-image-wrapper {
                position: absolute;
                width: 300px;
                height: 300px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.3) 100%);
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .mini-image-wrapper img {
                width: 100%;
                height: 100%;
                object-fit: contain;
            }

            .mini-left-image {
                left: 0;
                border-radius: 15px 0 0 15px;
            }

            .mini-right-image {
                right: 0;
                border-radius: 0 15px 15px 0;
            }

            .mini-result-image {
                width: 600px;
                height: 300px;
                position: absolute;
                left: 0;
                top: 0;
                border-radius: 15px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.25);
                background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0.3) 100%);
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .mini-result-image img {
                width: 100%;
                height: 100%;
                object-fit: contain;
                border-radius: 15px;
            }

            /* Animations for Set 1 */
            .mini-left-image.set1 {
                animation: miniLeftSet1 18s infinite linear;
            }

            .mini-right-image.set1 {
                animation: miniRightSet1 18s infinite linear;
            }

            .mini-result-image.set1 {
                animation: miniResultSet1 18s infinite linear;
            }

            /* Animations for Set 2 */
            .mini-left-image.set2 {
                animation: miniLeftSet2 18s infinite linear;
            }

            .mini-right-image.set2 {
                animation: miniRightSet2 18s infinite linear;
            }

            .mini-result-image.set2 {
                animation: miniResultSet2 18s infinite linear;
            }

            /* Animations for Set 3 */
            .mini-left-image.set3 {
                animation: miniLeftSet3 18s infinite linear;
            }

            .mini-right-image.set3 {
                animation: miniRightSet3 18s infinite linear;
            }

            .mini-result-image.set3 {
                animation: miniResultSet3 18s infinite linear;
            }

            /* Set 1 Keyframes (0-6s of 18s) */
            @keyframes miniLeftSet1 {
                0% {
                    transform: translateX(-120px) rotateY(15deg);
                    opacity: 0;
                }
                5% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                22% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                28% {
                    transform: translateX(0) rotateY(0);
                    opacity: 0;
                }
                33%, 100% {
                    transform: translateX(-120px) rotateY(15deg);
                    opacity: 0;
                }
            }

            @keyframes miniRightSet1 {
                0% {
                    transform: translateX(120px) rotateY(-15deg);
                    opacity: 0;
                }
                5% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                22% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                28% {
                    transform: translateX(0) rotateY(0);
                    opacity: 0;
                }
                33%, 100% {
                    transform: translateX(120px) rotateY(-15deg);
                    opacity: 0;
                }
            }

            @keyframes miniResultSet1 {
                0%, 22% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
                28% {
                    opacity: 1;
                    transform: scale(1.05);
                    z-index: 10;
                }
                30% {
                    opacity: 1;
                    transform: scale(1);
                    z-index: 10;
                }
                32% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
                33%, 100% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
            }

            /* Set 2 Keyframes (6-12s of 18s) */
            @keyframes miniLeftSet2 {
                0%, 33% {
                    transform: translateX(-120px) rotateY(15deg);
                    opacity: 0;
                }
                38% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                55% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                61% {
                    transform: translateX(0) rotateY(0);
                    opacity: 0;
                }
                66%, 100% {
                    transform: translateX(-120px) rotateY(15deg);
                    opacity: 0;
                }
            }

            @keyframes miniRightSet2 {
                0%, 33% {
                    transform: translateX(120px) rotateY(-15deg);
                    opacity: 0;
                }
                38% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                55% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                61% {
                    transform: translateX(0) rotateY(0);
                    opacity: 0;
                }
                66%, 100% {
                    transform: translateX(120px) rotateY(-15deg);
                    opacity: 0;
                }
            }

            @keyframes miniResultSet2 {
                0%, 55% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
                61% {
                    opacity: 1;
                    transform: scale(1.05);
                    z-index: 10;
                }
                63% {
                    opacity: 1;
                    transform: scale(1);
                    z-index: 10;
                }
                65% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
                66%, 100% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
            }

            /* Set 3 Keyframes (12-18s of 18s) */
            @keyframes miniLeftSet3 {
                0%, 66% {
                    transform: translateX(-120px) rotateY(15deg);
                    opacity: 0;
                }
                72% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                88% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                94% {
                    transform: translateX(0) rotateY(0);
                    opacity: 0;
                }
                100% {
                    transform: translateX(-120px) rotateY(15deg);
                    opacity: 0;
                }
            }

            @keyframes miniRightSet3 {
                0%, 66% {
                    transform: translateX(120px) rotateY(-15deg);
                    opacity: 0;
                }
                72% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                88% {
                    transform: translateX(0) rotateY(0);
                    opacity: 1;
                }
                94% {
                    transform: translateX(0) rotateY(0);
                    opacity: 0;
                }
                100% {
                    transform: translateX(120px) rotateY(-15deg);
                    opacity: 0;
                }
            }

            @keyframes miniResultSet3 {
                0%, 88% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
                94% {
                    opacity: 1;
                    transform: scale(1.05);
                    z-index: 10;
                }
                96% {
                    opacity: 1;
                    transform: scale(1);
                    z-index: 10;
                }
                98% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
                100% {
                    opacity: 0;
                    transform: scale(0.8);
                    z-index: -1;
                }
            }

            .mini-progress-bar {
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                width: 300px;
                height: 4px;
                background: rgba(255, 165, 0, 0.2);
                border-radius: 2px;
                overflow: hidden;
            }

            .mini-progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #ffa502 0%, #ff6348 100%);
                border-radius: 2px;
                animation: miniProgressCycle 18s linear infinite;
            }

            @keyframes miniProgressCycle {
                0% { width: 0%; }
                100% { width: 100%; }
            }

            .animation-title {
                position: absolute;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                color: #ff6348;
                font-size: 18px;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(255,99,72,0.2);
                z-index: 100;
            }
        </style>

        <div class="animation-container">
            <div class="animation-title">Nano Banana Magic ✨</div>
            <div class="mini-container" id="animContainer">
                <!-- Set 1 Images -->
                <div class="mini-image-wrapper mini-left-image set1" style="animation-play-state: running;">
                    <img src="/gradio_api/file=one-1.png" alt="Set1 Left"> <!--src would be file/my_image.png*/ -->
                </div>
                <div class="mini-image-wrapper mini-right-image set1" style="animation-play-state: running;">
                    <img src="/gradio_api/file=one-2.png" alt="Set1 Right">
                </div>
                <div class="mini-result-image set1" style="animation-play-state: running;">
                    <img src="/gradio_api/file=one-3.jpg" alt="Set1 Result">
                </div>

                <!-- Set 2 Images -->
                <div class="mini-image-wrapper mini-left-image set2" style="animation-play-state: running;">
                    <img src="/gradio_api/file=two-1.png" alt="Set2 Left">
                </div>
                <div class="mini-image-wrapper mini-right-image set2" style="animation-play-state: running;">
                    <img src="/gradio_api/file=two-2.png" alt="Set2 Right">
                </div>
                <div class="mini-result-image set2" style="animation-play-state: running;">
                    <img src="/gradio_api/file=two-3.jpeg" alt="Set2 Result">
                </div>

                <!-- Set 3 Images -->
                <div class="mini-image-wrapper mini-left-image set3" style="animation-play-state: running;">
                    <img src="/gradio_api/file=three-1.png" alt="Set3 Left">
                </div>
                <div class="mini-image-wrapper mini-right-image set3" style="animation-play-state: running;">
                    <img src="/gradio_api/file=three-2.png" alt="Set3 Right">
                </div>
                <div class="mini-result-image set3" style="animation-play-state: running;">
                    <img src="/gradio_api/file=three-3.jpg" alt="Set3 Result">
                </div>

                <!-- Progress bar -->
                <div class="mini-progress-bar">
                    <div class="mini-progress-fill" style="animation-play-state: running;"></div>
                </div>
            </div>
        </div>

        <script>
            // Force restart animations on load
            setTimeout(function() {
                const elements = document.querySelectorAll('.mini-image-wrapper, .mini-result-image, .mini-progress-fill');
                elements.forEach(el => {
                    el.style.animationPlayState = 'running';
                });
            }, 100);
        </script>
        """
    )

# Create the Gradio interface
with gr.Blocks(theme='ocean') as demo:
    # Add navigation bar
    navbar = gr.Navbar(
        value=[
            ("Github repo", "https://github.com/Marvel202/banana-app/tree/main"),
            ("Learn more about Gradio Navbar", "https://www.gradio.app/guides/multipage-apps#customizing-the-navbar")
        ],
        visible=True,
        main_page_name="🎨 guided nano banana"
    )
    with gr.Row():
        # Add the animated banner
        examples_image_banner.render()

        with gr.Column():
            gr.HTML(
                """
                <h1><center>🍌 Nano Banana Image Composer</center></h1>

                <b>How to use:</b><br>
                1. Upload or capture the first image and draw a box where you want to place an object<br>
                2. Upload the second image containing the object you want to insert<br>
                3. Click "Generate Composite Image" and wait for Gemini's Nano Banana model to blend the images<br>

                <br>The Gradio app will intelligently place the object from the second image into the boxed area of the first image,
                taking care of lighting, shadows, and proper integration using Google's advanced Nano Banana technology.<br>
                <br>Kindly note that this app is experimental, so image edits might not always create the desired results.
                """
            )

            # Debug Configuration
            with gr.Accordion("� Debug & Configuration", open=False):
                gr.Markdown(
                    """
                    **Debug Mode:** Enable to see detailed processing information and troubleshoot issues.
                    
                    **Google API:** This app uses your Google API key from the .env file to access Gemini's Nano Banana model.
                    
                    **Note:** Make sure your Google API key has access to the Gemini image generation models.
                    """
                )
                debug_checkbox = gr.Checkbox(
                    label="🐛 Enable Debug Mode",
                    value=False,
                    info="Show detailed debugging information during processing"
                )

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Step 1: Annotate First Image _(click on the upload image button if the app is stuck)_")
                    # Image annotator for first image
                    from gradio_image_annotation import image_annotator
                    #first_image = ImageAnnotator(
                    first_image = image_annotator(
                        value=None,
                        label="Draw a box where you want to place the object",
                        image_type="pil",
                        single_box=True,  # Only allow one box
                        disable_edit_boxes=True,
                        show_download_button=False,
                        show_share_button=False,
                        box_thickness=3,
                        box_selected_thickness=4,
                        show_label=True,
                        #image_mode="RGB",
                        #box_min_size=20,
                    )

                with gr.Column(scale=1):
                    gr.Markdown("### Step 2: Upload Second Image")
                    # Regular image input for second image
                    second_image = gr.Image(
                        label="Image containing the object to insert",
                        type="numpy",
                        height=400,
                    )
                    # Generate button
                    generate_btn = gr.Button("Step 3: 🚀 Generate Composite Image", variant="primary", size="lg")
                    
                    # Test button for debugging
                    test_btn = gr.Button("🧪 Test Interface", variant="secondary", size="sm")

    # Output section
    with gr.Column():
        output_image = gr.Image(
            label="Generated Composite Image",
            type="filepath",
            height=500,
        )
        # Add download button
        with gr.Row():
            download_btn = gr.Button("💾 Download Latest Generated PNG", variant="secondary", size="lg")
        
        status_text = gr.Textbox(
            label="Status",
            placeholder="Results will appear here...",
            lines=3,
        )

    # Connect the button to the processing function
    generate_btn.click(
        fn=process_images,
        inputs=[first_image, second_image, debug_checkbox],
        outputs=[output_image, status_text],
        show_progress=True,
    )
    
    # Connect the download button to provide the PNG file
    download_btn.click(
        fn=download_image,
        inputs=[],
        outputs=gr.File(label="Download PNG")
    )
    
    # Connect the test button
    test_btn.click(
        fn=simple_interface_test,
        inputs=[],
        outputs=[output_image, status_text]
    )

    examples = [
        [
            {
                "image": "examples/example1-1.png",
                "boxes": [{"xmin": 61, "ymin": 298, "xmax": 228, "ymax": 462}],
            },
            "examples/example1-2.png",
        ],
        [
            {
                "image": "examples/example2-1.png",
                "boxes": [{"xmin": 205, "ymin": 791, "xmax": 813, "ymax": 1161}],
            },
            "examples/example2-2.jpg",
        ],
        [
            {
                "image": "examples/example3-1.png",
                "boxes": [{"xmin": 24, "ymin": 465, "xmax": 146, "ymax": 607}],
            },
            "examples/example3-2.png",
        ],
    ]
    
    ex = gr.Examples(
        examples=examples,
        inputs=[first_image, second_image],
    )


with demo.route("ℹ️Tips for Best Results", "/tips"):
    gr.Markdown(
        """
        # ℹ️ Tips for Best Results
        - **Box Placement**: Draw the box exactly where you want the object to appear
        - **Image Quality**: Use high-resolution images for better results
        - **Object Selection**: The second image should clearly show the object you want to insert
        - **Lighting**: Images with similar lighting conditions work best
        - **Processing Time**: Generation typically takes 10-60 seconds with Gemini's Nano Banana model
        - **Debug Mode**: Enable debug mode if you encounter issues to see detailed processing information
        - **API Key**: Make sure your Google API key has access to Gemini image generation models
        """
    )

    # Different navbar for the Settings page
    navbar = gr.Navbar(
        visible=True,
        main_page_name="Home",
    )

if __name__ == "__main__":
    demo.launch(ssr_mode=False, allowed_paths=["."], debug=False)