import streamlit as st
import cv2
import numpy as np
import requests
import tempfile
import os

def extract_frames(video_path, num_frames=6):
    """
    Extract evenly spaced frames from a video
    
    Args:
        video_path (str): Path to the video file
        num_frames (int): Number of frames to extract
    
    Returns:
        list: List of extracted frames as numpy arrays
    """
    # Open the video
    cap = cv2.VideoCapture(video_path)
    
    # Get total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate frame indices to extract
    frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
    
    # List to store extracted frames
    extracted_frames = []
    
    # Extract frames
    for index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ret, frame = cap.read()
        
        if ret:
            # Convert frame from BGR to RGB (for proper color representation)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            extracted_frames.append(frame_rgb)
    
    cap.release()
    return extracted_frames

def send_frame_to_api(frame):
    """
    Send a single frame to the API for plaque detection
    
    Args:
        frame (numpy.ndarray): Frame to send
    
    Returns:
        dict: API response or None
    """
    try:
        # Encode frame to PNG
        _, buffer = cv2.imencode('.png', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
        # Prepare files for upload
        files = {'image': ('frame.png', buffer.tobytes(), 'image/png')}
        
        # Replace with your actual API endpoint
        api_url = "https://your-plaque-detection-api.com/detect"
        
        # Send POST request
        response = requests.post(api_url, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request failed. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        st.error(f"Error mandando el cuadro al sistema: {e}")
        return None

def main():
    # Set page configuration
    st.set_page_config(page_title="Detector de placas para infraccion", page_icon=":police:")
    
    # Main title
    st.title("Levante la multa a la placa correspondiente")
    
    # Video file uploader
    uploaded_file = st.file_uploader(
        "Escoge el video", 
        type=['mp4','mov', 'mkv'],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Create a temporary file to save the uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            video_path = tmp_file.name
        
        # Display file details
        file_details = {
            "Nombre del archivo": uploaded_file.name,
            "Extensión del video": uploaded_file.type,
            "Tamaño del video": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write("Detalles del video:")
        st.json(file_details)
        
        # Button to process video
        if st.button("Deteccion de placas"):
            try:
                # Extract frames
                st.write("Extrayendo cuadros...")
                frames = extract_frames(video_path)
                
                # Display extracted frames
                st.write("Cuadros extraidos:")
                frame_columns = st.columns(6)
                for i, frame in enumerate(frames):
                    with frame_columns[i]:
                        st.image(frame, caption=f"Frame {i+1}")
                
                # Detect plaques
                st.write("Mandando los cuadros del video...")
                plaque_results = []
                progress_bar = st.progress(0)
                
                for i, frame in enumerate(frames):
                    # Send frame to API
                    result = send_frame_to_api(frame)
                    
                    if result:
                        plaque_results.append({
                            "frame": i+1,
                            "plaques": result.get('plaques', [])
                        })
                    
                    # Update progress
                    progress_bar.progress((i+1) / len(frames))
                
                # Display plaque detection results
                st.write("Resultado de la detección de placa:")
                for result in plaque_results:
                    st.write(f"Cuadro {result['frame']}:")
                    if result['plaques']:
                        for plaque in result['plaques']:
                            st.write(f"- Placa detectada: {plaque}")
                    else:
                        st.write("No se detectaron placas")
                
            except Exception as e:
                st.error(f"Error en el procesamiento del video: {e}")
            
            finally:
                # Clean up temporary file
                os.unlink(video_path)

if __name__ == "__main__":
    main()