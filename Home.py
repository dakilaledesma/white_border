import streamlit as st
from PIL import Image
import io
import zipfile

def add_border(image, h_padding, v_padding, border_width, border_height):
    width, height = image.size
    
    # Ensure border is larger than the original image
    new_width = max(border_width, int(width * (1 + 2 * h_padding)))
    new_height = max(border_height, int(height * (1 + 2 * v_padding)))
    
    # Create the white border image
    result = Image.new(image.mode, (new_width, new_height), (255, 255, 255))
    
    # Calculate position to paste the original image
    paste_x = (new_width - width) // 2
    paste_y = (new_height - height) // 2
    
    # Paste the original image onto the white background
    result.paste(image, (paste_x, paste_y))
    
    return result

def fit_to_aspect_ratio(image, target_width, target_height):
    width, height = image.size
    target_ratio = target_width / target_height
    current_ratio = width / height
    
    if current_ratio > target_ratio:
        new_width = width
        new_height = int(width / target_ratio)
    else:
        new_height = height
        new_width = int(height * target_ratio)
    
    # Resize the image to fit the target aspect ratio
    return image.resize((new_width, new_height), Image.LANCZOS)

st.title("White Border")
st.text("Written for Tatiana bc she is incapable of using GIMP 😔✊")

uploaded_files = st.file_uploader("Upload image files (don't ZIP them, you can upload multiple files at once)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

with st.expander("Portrait Settings"):
    st.subheader("Portrait Settings")
    portrait_keep_original_aspect = st.checkbox("Keep original image aspect (Portrait)", value=True, key="portrait_keep_aspect")
    
    if not portrait_keep_original_aspect:
        portrait_image_width_aspect = st.number_input("Image width aspect (Portrait)", min_value=1, value=8, step=1, key="portrait_image_width")
        portrait_image_height_aspect = st.number_input("Image height aspect (Portrait)", min_value=1, value=11, step=1, key="portrait_image_height")
    
    portrait_border_width_aspect = st.number_input("Border width aspect (Portrait)", min_value=1, value=9, step=1, key="portrait_border_width")
    portrait_border_height_aspect = st.number_input("Border height aspect (Portrait)", min_value=1, value=12, step=1, key="portrait_border_height")

    st.subheader("Portrait Border Padding Settings")
    portrait_h_padding = st.number_input("Horizontal padding percent (Portrait)", min_value=0.0, max_value=1.0, value=0.1, step=0.01, key="portrait_h_padding")
    portrait_v_padding = st.number_input("Vertical padding percent (Portrait)", min_value=0.0, max_value=1.0, value=0.1, step=0.01, key="portrait_v_padding")

with st.expander("Landscape Settings"):
    st.subheader("Landscape Settings")
    landscape_keep_original_aspect = st.checkbox("Keep original image aspect (Landscape)", value=True, key="landscape_keep_aspect")
    
    if not landscape_keep_original_aspect:
        landscape_image_width_aspect = st.number_input("Image width aspect (Landscape)", min_value=1, value=11, step=1, key="landscape_image_width")
        landscape_image_height_aspect = st.number_input("Image height aspect (Landscape)", min_value=1, value=8, step=1, key="landscape_image_height")
    
    landscape_border_width_aspect = st.number_input("Border width aspect (Landscape)", min_value=1, value=12, step=1, key="landscape_border_width")
    landscape_border_height_aspect = st.number_input("Border height aspect (Landscape)", min_value=1, value=9, step=1, key="landscape_border_height")

    st.subheader("Landscape Border Padding Settings")
    landscape_h_padding = st.number_input("Horizontal padding percent (Landscape)", min_value=0.0, max_value=1.0, value=0.1, step=0.01, key="landscape_h_padding")
    landscape_v_padding = st.number_input("Vertical padding percent (Landscape)", min_value=0.0, max_value=1.0, value=0.1, step=0.01, key="landscape_v_padding")

if st.button("Process Images") and uploaded_files:
    processed_images = []
    
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        original_width, original_height = image.size
        is_portrait = original_height > original_width
        
        if is_portrait:
            keep_original_aspect = portrait_keep_original_aspect
            image_width_aspect = portrait_image_width_aspect if not keep_original_aspect else original_width
            image_height_aspect = portrait_image_height_aspect if not keep_original_aspect else original_height
            border_width_aspect = portrait_border_width_aspect
            border_height_aspect = portrait_border_height_aspect
            h_padding = portrait_h_padding
            v_padding = portrait_v_padding
        else:
            keep_original_aspect = landscape_keep_original_aspect
            image_width_aspect = landscape_image_width_aspect if not keep_original_aspect else original_width
            image_height_aspect = landscape_image_height_aspect if not keep_original_aspect else original_height
            border_width_aspect = landscape_border_width_aspect
            border_height_aspect = landscape_border_height_aspect
            h_padding = landscape_h_padding
            v_padding = landscape_v_padding
        
        if not keep_original_aspect:
            image = fit_to_aspect_ratio(image, image_width_aspect, image_height_aspect)
        
        width, height = image.size
        border_width = int(width * (border_width_aspect / image_width_aspect))
        border_height = int(height * (border_height_aspect / image_height_aspect))
        
        bordered_image = add_border(image, h_padding, v_padding, border_width, border_height)
        
        img_byte_arr = io.BytesIO()
        bordered_image.save(img_byte_arr, format='PNG')
        processed_images.append((uploaded_file.name, img_byte_arr.getvalue()))
    
    if processed_images:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for filename, img_bytes in processed_images:
                zip_file.writestr(f"bordered_{filename}", img_bytes)
        
        st.download_button(
            label="Download processed files",
            data=zip_buffer.getvalue(),
            file_name="bordered_images.zip",
            mime="application/zip"
        )
        
        st.success(f"Processed {len(processed_images)} images. Click the button above to download.")