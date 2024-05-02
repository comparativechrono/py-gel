import streamlit as st
import numpy as np
import cv2
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

def auto_detect_bands(image):
    """Automatically detect bands in the gel image using image processing"""
    img_array = np.array(image)
    # Convert to binary using Otsu's thresholding
    _, thresh = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Find contours (bands)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rois = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 20 and h > 20:  # Filter out too small contours
            rois.append((x, y, x+w, y+h))
    return rois

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

        # Define interface for manual ROI adjustments
        with st.sidebar:
            st.write("Manual ROI Coordinates")
            x_start = st.slider('Start X', min_value=0, max_value=image.width, value=0)
            y_start = st.slider('Start Y', min_value=0, max_value=image.height, value=0)
            x_end = st.slider('End X', min_value=0, max_value=image.width, value=int(image.width/2))
            y_end = st.slider('End Y', min_value=0, max_value=image.height, value=int(image.height/2))
            roi_name = st.text_input("Name this ROI", "")

        # Store multiple ROIs
        if 'roi_list' not in st.session_state:
            st.session_state.roi_list = {}

        # Buttons for auto-detection and manual ROI management
        if st.button('Auto-detect Bands'):
            auto_rois = auto_detect_bands(image)
            for i, roi_coords in enumerate(auto_rois):
                name = f'Auto-{i}'
                st.session_state.roi_list[name] = {'coords': roi_coords}

        if st.button("Confirm ROI") and roi_name:
            st.session_state.roi_list[roi_name] = {'coords': (x_start, y_start, x_end, y_end)}

        # Display image with all ROIs
        fig, ax = plt.subplots()
        ax.imshow(img_array, cmap='gray')
        for name, roi in st.session_state.roi_list.items():
            coords = roi['coords']
            rect = plt.Rectangle((coords[0], coords[1]), coords[2] - coords[0], coords[3] - coords[1], linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        # Temporary ROI for visualization (blue dashed rectangle)
        rect = plt.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, linewidth=1, edgecolor='b', facecolor='none', linestyle="--")
        ax.add_patch(rect)
        st.pyplot(fig)

        # Display intensities for all ROIs
        if st.button('Calculate Intensities for All ROIs'):
            results = []
            for name, roi in st.session_state.roi_list.items():
                total_intensity, mean_intensity = calculate_intensity(image, roi['coords'])
                results.append(f'ROI "{name}": Total Intensity = {total_intensity}, Mean Intensity = {mean_intensity} (Intensity per pixel)')
            for result in results:
                st.write(result)

if __name__ == '__main__':
    main()
