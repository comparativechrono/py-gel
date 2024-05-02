import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt

def calculate_intensity(image, roi_coords):
    """Calculate the mean intensity of the selected ROI"""
    x_start, y_start, width, height = roi_coords
    roi = image.crop((x_start, y_start, x_start + width, y_start + height))
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

        img_array = np.array(image)
        
        # Store multiple ROIs
        if 'roi_list' not in st.session_state:
            st.session_state.roi_list = []

        # Sliders for adjusting ROI dynamically
        x_start = st.slider('Start X', min_value=0, max_value=image.width, value=0)
        y_start = st.slider('Start Y', min_value=0, max_value=image.height, value=0)
        width = st.slider('Width', min_value=1, max_value=image.width - x_start, value=100)
        height = st.slider('Height', min_value=1, max_value=image.height - y_start, value=100)

        # Display image with all ROIs
        fig, ax = plt.subplots()
        ax.imshow(img_array, cmap='gray')
        for roi in st.session_state.roi_list:
            rect = plt.Rectangle((roi[0], roi[1]), roi[2], roi[3], linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        # Temporary ROI for visualization
        rect = plt.Rectangle((x_start, y_start), width, height, linewidth=1, edgecolor='b', facecolor='none', linestyle="--")
        ax.add_patch(rect)
        st.pyplot(fig)

        # Confirm or discard the temporary ROI
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm ROI"):
                st.session_state.roi_list.append((x_start, y_start, width, height))
        with col2:
            if st.button("Discard ROI"):
                # Just redisplay the image without adding the ROI
                st.experimental_rerun()

        # Display intensities for all ROIs
        if st.button('Calculate Intensities for All ROIs'):
            results = []
            for roi in st.session_state.roi_list:
                intensity = calculate_intensity(image, roi)
                results.append(f'ROI at ({roi[0]}, {roi[1]}, {roi[2]}, {roi[3]}) - Intensity: {intensity}')
            for result in results:
                st.write(result)

if __name__ == '__main__':
    main()
