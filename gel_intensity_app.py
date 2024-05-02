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

def auto_detect_bands(image, min_size, max_size):
    """Automatically detect bands using adaptive thresholding and morphology"""
    img_array = np.array(image)
    img_blur = cv2.GaussianBlur(img_array, (5, 5), 0)
    img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))  # Adjust size based on expected band orientation
    img_morph = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(img_morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rois = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if min_size <= w*h <= max_size:
            rois.append((x, y, x+w, y+h))
    return rois

def main():
    st.title('Gel Band Intensity Analyzer')

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('L')
        
        invert = st.checkbox("Invert image colors")
        if invert:
            image = ImageOps.invert(image)

        img_array = np.array(image)

        # Sidebar for controls
        with st.sidebar:
            st.write("Manual ROI Coordinates")
            x_start = st.slider('Start X', min_value=0, max_value=image.width, value=0)
            y_start = st.slider('Start Y', min_value=0, max_value=image.height, value=0)
            x_end = st.slider('End X', min_value=0, max_value=image.width, value=int(image.width/2))
            y_end = st.slider('End Y', min_value=0, max_value=image.height, value=int(image.height/2))
            roi_name = st.text_input("Name this ROI", "")

            st.write("Auto-Detect Settings")
            min_size = st.slider("Min Size", min_value=10, max_value=1000, value=100, step=10)
            max_size = st.slider("Max Size", min_value=100, max_value=5000, value=1000, step=10)
            auto_detect = st.button('Auto-detect Bands')

        if 'roi_list' not in st.session_state:
            st.session_state.roi_list = {}

        # Auto-detection and manual confirmation buttons
        if auto_detect:
            auto_rois = auto_detect_bands(image, min_size, max_size)
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
        st.pyplot(fig)

        # Intensity calculations
        if st.button('Calculate Intensities for All ROIs'):
            results = []
            for name, roi in st.session_state.roi_list.items():
                total_intensity, mean_intensity = calculate_intensity(image, roi['coords'])
                results.append(f'ROI "{name}": Total Intensity = {total_intensity}, Mean Intensity = {mean_intensity} (Intensity per pixel)')
            for result in results:
                st.write(result)

if __name__ == '__main__':
    main()
