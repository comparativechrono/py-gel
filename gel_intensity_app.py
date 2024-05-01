import streamlit as st
import cv2
import numpy as np
from PIL import Image

def calculate_intensity(roi):
    """Calculate the mean intensity of the selected ROI."""
    return np.mean(roi)

def main():
    st.title('Gel Band Intensity Analyzer')

    # Upload an image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert('L')  # Convert image to grayscale
            image_array = np.array(image)

            # Display the image
            st.image(image, caption='Uploaded Image.', use_column_width=True)

            # Select ROI coordinates via sliders
            st.write("Select the Region of Interest (ROI) coordinates:")
            cols = st.columns(2)
            x_start = cols[0].slider('Start X', min_value=0, max_value=image.width, value=0)
            x_end = cols[0].slider('End X', min_value=0, max_value=image.width, value=int(image.width/2))
            y_start = cols[1].slider('Start Y', min_value=0, max_value=image.height, value=0)
            y_end = cols[1].slider('End Y', min_value=0, max_value=image.height, value=int(image.height/2))

            # Button to calculate intensity
            if st.button('Calculate Intensity'):
                if x_end > x_start and y_end > y_start:
                    roi = image_array[y_start:y_end, x_start:x_end]
                    intensity = calculate_intensity(roi)
                    st.write(f'Average Intensity: {intensity}')
                else:
                    st.error('Invalid ROI coordinates. Please ensure that End X > Start X and End Y > Start Y.')
        except Exception as e:
            st.error(f"Error processing the image: {e}")
    else:
        st.write("No image uploaded yet. Please upload an image.")

if __name__ == '__main__':
    main()
