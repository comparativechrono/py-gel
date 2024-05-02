import streamlit as st
import numpy as np
from PIL import Image, ImageOps, ImageDraw

def calculate_intensity(roi):
    """ Calculate the mean intensity of the selected ROI """
    return np.mean(np.array(roi))

def main():
    st.title('Gel Band Intensity Analyzer')

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('L')  # Convert image to grayscale
        
        # Invert colors option
        invert = st.checkbox("Invert image colors")
        if invert:
            image = ImageOps.invert(image)
        
        # Displaying the image
        img_array = np.array(image)
        st.image(img_array, caption='Uploaded Image.', use_column_width=True)

        # ROI selection
        roi_details = st.text_input("Enter ROI coordinates as x_start, y_start, width, height", "0,0,100,100")
        try:
            x_start, y_start, width, height = map(int, roi_details.split(','))
            x_end = x_start + width
            y_end = y_start + height
            if x_end <= image.width and y_end <= image.height:
                img_copy = image.copy()
                draw = ImageDraw.Draw(img_copy)
                draw.rectangle([x_start, y_start, x_end, y_end], outline="red", width=2)
                st.image(img_copy, caption='ROI Selected', use_column_width=True)
                
                if st.button('Calculate Intensity'):
                    roi = image.crop((x_start, y_start, x_end, y_end))
                    intensity = calculate_intensity(roi)
                    st.write(f'ROI Intensity: {intensity}')
            else:
                st.error("ROI coordinates are out of image bounds.")
        except:
            st.error("Invalid ROI format. Please enter as x_start, y_start, width, height.")

if __name__ == '__main__':
    main()
