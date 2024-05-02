import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import cv2

def calculate_intensity(image, roi_coords):
    """Calculate the mean and total intensity of the selected ROI"""
    x_start, y_start, x_end, y_end = roi_coords
    roi = image.crop((x_start, y_start, x_end, y_end))
    roi_array = np.array(roi)
    total_intensity = np.sum(roi_array)
    mean_intensity = np.mean(roi_array)
    return total_intensity, mean_intensity

def find_bands(image, percentile_threshold, continuity, min_band_length):
    """Auto-detect bands based on the provided scanning approach"""
    gel_array = np.array(image)
    intensity_threshold = np.percentile(gel_array, percentile_threshold)
    high_intensity_y = []

    # Scan each column
    for x in range(gel_array.shape[1]):
        column = gel_array[:, x]
        max_intensity_y = np.argmax(column)
        if column[max_intensity_y] >= intensity_threshold:
            high_intensity_y.append((x, max_intensity_y))

    # Group high-intensity points
    bands = []
    current_band = [high_intensity_y[0]]

    for i in range(1, len(high_intensity_y)):
        previous_point = high_intensity_y[i - 1]
        current_point = high_intensity_y[i]
        if current_point[0] == previous_point[0] + 1 and abs(current_point[1] - previous_point[1]) <= continuity:
            current_band.append(current_point)
        else:
            if len(current_band) > min_band_length:
                bands.append(current_band)
            current_band = [current_point]

    if len(current_band) > min_band_length:
        bands.append(current_band)

    return bands

def main():
    st.title('Gel Band Intensity Analyzer')

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('L')
        
        invert = st.checkbox("Invert image colors")
        if invert:
            image = ImageOps.invert(image)

        img_array = np.array(image)  # Use the original image for display and calculations

        with st.sidebar:
            st.write("Manual ROI Coordinates")
            x_start = st.slider('Start X', min_value=0, max_value=image.width, value=0)
            y_start = st.slider('Start Y', min_value=0, max_value=image.height, value=0)
            x_end = st.slider('End X', min_value=0, max_value=image.width, value=image.width // 2)
            y_end = st.slider('End Y', min_value=0, max_value=image.height, value=image.height // 2)
            roi_name = st.text_input("Name this ROI", "")
            confirm_roi = st.button("Confirm ROI")
            
            st.write("Auto-Detect Settings")
            percentile_threshold = st.slider("Intensity Percentile", min_value=80, max_value=99, value=95)
            continuity = st.slider("Continuity", min_value=1, max_value=5, value=2)
            min_band_length = st.slider("Minimum Band Length", min_value=3, max_value=20, value=5)
            auto_detect = st.button('Auto-detect Bands')
            clear_rois = st.button('Clear All ROIs')

        if 'roi_list' not in st.session_state:
            st.session_state.roi_list = {}

        if clear_rois:
            st.session_state.roi_list = {}

        if auto_detect:
            st.session_state.bands = find_bands(image, percentile_threshold, continuity, min_band_length)

        if confirm_roi and roi_name:
            st.session_state.roi_list[roi_name] = {'coords': (x_start, y_start, x_end, y_end)}

        # Display image with detected bands and manual ROIs
        fig, ax = plt.subplots()
        ax.imshow(img_array, cmap='gray')

        for band in getattr(st.session_state, 'bands', []):
            xs, ys = zip(*band)
            ax.plot(xs, ys, 'r-', linewidth=2)

        for name, roi in st.session_state.roi_list.items():
            coords = roi['coords']
            rect = plt.Rectangle((coords[0], coords[1]), coords[2] - coords[0], coords[3] - coords[1], linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        ax.set_title('Detected Bands and ROIs in Gel Image')
        ax.axis('off')
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
