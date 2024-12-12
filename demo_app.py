import streamlit as st
import requests
import numpy as np
from PIL import Image
import io

def send_image_to_api(uploaded_file):
    """
    Send image to API for processing
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        API response or None
    """
    try:
        # Read the image file
        image = Image.open(uploaded_file)
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr = img_byte_arr.getvalue()
        
        # Prepare files for upload
        files = {'image': (uploaded_file.name, img_byte_arr, uploaded_file.type)}
        
        # Replace with your actual API endpoint
        api_url = "http://3.20.238.57:80/detect" 
        #CAMBIAR CON EL ENDPOINT DE LA API NUESTRA

        # Send POST request
        response = requests.post(api_url, files=files)
        
        # Check response
        if response.status_code == 200:
            st.success("¡Imagen subida con éxito!")
            return response.json()
        else:
            st.error(f"Publicación fallida. Error: {response.status_code}")
            return None
    
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        return None

def main():
    # Set page configuration
    st.set_page_config(page_title="Levantamiento de placas", page_icon=":car:")
    
    # Main title
    st.title("LECTURA DE PLACAS PARA INFRACCION (IMAGENES)")
    
    # Image file uploader
    uploaded_files = st.file_uploader(
        "Selecciona la foto", 
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True
    )
    
    # Process uploaded images
    if uploaded_files:
        # Create columns for images
        num_cols = min(3, len(uploaded_files))
        columns = st.columns(num_cols)
        
        # Process each uploaded image
        for i, uploaded_file in enumerate(uploaded_files):
            # Determine which column to use
            col = columns[i % num_cols]
            
            with col:
                # Display the image
                st.image(uploaded_file, caption=uploaded_file.name)
                
                # File details
                file_details = {
                    "Nombre de archivo": uploaded_file.name,
                    "Extensión de la foto": uploaded_file.type,
                    "Tamaño de la foto": f"{uploaded_file.size / 1024:.2f} KB"
                }
                st.json(file_details)
                
                # Upload button for individual image
                if st.button(f"Sube la imagen {uploaded_file.name}"):
                    # Send image to API
                    response = send_image_to_api(uploaded_file)
                    
                    # Display API response
                    if response:
                        st.write("API Response:")
                        st.json(response)

if __name__ == "__main__":
    main()