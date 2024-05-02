import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt

def calculate_intensity(image, roi_coords):
    """Calculate the mean and total intensity of the selected ROI"""
    x_start, y_start, x_end, y_end = roi_coords
    roi = image.crop((x_start, y_start, x_end, y_end))
    roi_array = np.array(roi)
    total_intensity = np.sum(roi_array)
    mean_intensity = np.mean(roi_array)
    return total_intensity, mean_intensity

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

        # Define interface for ROI adjustments
        with st.sidebar:
            st.write("Adjust ROI Coordinates")
            x_start = st.slider('Start X', min_value=0, max_value=image.width, value=0, key='x_start')
            x_end = st.slider('End X', min_value=0, max_value=image.width, value=int(image.width/2), key='x_end')
            y_start = st.slider('Start Y', min_value=0, max_value=image.height, value=0, key='y_start')
            y_end = st.slider('End Y', min_value=0, max_value=image.height, value=int(image.height/2), key='y_end')
            roi_name = st.text_input("Name this ROI", "")

        # Store multiple ROIs
        if 'roi_list' not in st.session_state:
            st.session_state.roi_list = {}

        # Display image with all ROIs
        fig, ax = plt.subplots()
        ax.imshow(img_array, cmap='gray')
        for roi in st.session_state.roi_list.values():
            rect = plt.Rectangle((roi['coords'][0], roi['coords'][1]), roi['coords'][2] - roi['coords'][0], roi['coords'][3] - roi['coords'][1], linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        # Temporary ROI for visualization
        rect = plt.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, linewidth=1, edgecolor='b', facecolor='none', linestyle="--")
        ax.add_patch(rect)
        st.pyplot(fig)

        # Confirm or discard the temporary ROI
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm ROI") and roi_name:
                st.session_state.roi_list[roi_name] = {'coords': (x_start, y_start, x_end, y_end)}
        with col2:
            if st.button("Discard ROI"):
                st.experimental_rerun()

        # Display intensities for all ROIs
        if st.button('Calculate Intensities for All ROIs'):
            for name, roi in st.session_state.roi_list.items():
                total_intensity, mean_intensity = calculate_intensity(image, roi['coords'])
                st.write(f'ROI "{name}": Total Intensity = {total_intensity}, Mean Intensity = {mean_intensity} (Intensity per pixel)')

if __name__ == '__main__':
    main()
