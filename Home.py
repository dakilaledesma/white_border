import streamlit as st
from PIL import Image
import io
import zipfile

def add_border(image, h_padding, v_padding):
    width, height = image.size
    new_width = int(width * (1 + 2 * h_padding))
    new_height = int(height * (1 + 2 * v_padding))
    result = Image.new(image.mode, (new_width, new_height), (255, 255, 255))
    result.paste(image, (int(width * h_padding), int(height * v_padding)))
    return result

def fit_to_aspect_ratio(image, target_ratio=8.5/11):
    width, height = image.size
    current_ratio = width / height
    
    if (current_ratio > 1 and target_ratio < 1) or (current_ratio < 1 and target_ratio > 1):
        target_ratio = 1 / target_ratio
    
    if current_ratio > target_ratio:
        new_height = height
        new_width = int(height * target_ratio)
    else:
        new_width = width
        new_height = int(width / target_ratio)
    
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    
    return image.crop((left, top, right, bottom))

st.title("White Border")
st.text("Written for Tatiana bc she is incapable of using GIMP 😔✊")

uploaded_files = st.file_uploader("Upload image files (don't ZIP them, you can upload multiple files at once)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

with st.expander("Settings"):
    st.subheader("Portrait Settings")
    portrait_h_padding = st.number_input("Portrait Horizontal padding percent", min_value=0.0, max_value=1.0, value=0.12, step=0.01, key="portrait_h")
    portrait_v_padding = st.number_input("Portrait Vertical padding percent", min_value=0.0, max_value=1.0, value=0.06, step=0.01, key="portrait_v")

    st.subheader("Landscape Settings")
    landscape_h_padding = st.number_input("Landscape Horizontal padding percent", min_value=0.0, max_value=1.0, value=0.06, step=0.01, key="landscape_h")
    landscape_v_padding = st.number_input("Landscape Vertical padding percent", min_value=0.0, max_value=1.0, value=0.12, step=0.01, key="landscape_v")

    fit_aspect_ratio = st.checkbox("Fit to 8.5 x 11 aspect ratio", value=True)

if st.button("Process Images") and uploaded_files:
    processed_images = []
    
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        
        width, height = image.size
        is_portrait = height > width
        
        if fit_aspect_ratio:
            image = fit_to_aspect_ratio(image)
        
        if is_portrait:
            bordered_image = add_border(image, portrait_h_padding, portrait_v_padding)
        else:
            bordered_image = add_border(image, landscape_h_padding, landscape_v_padding)
        
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