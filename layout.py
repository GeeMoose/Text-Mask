import streamlit as st
from PIL import Image
import io
import numpy as np

def adjust_image(image, brightness, contrast):
    img_array = np.array(image).astype(float)
    adjusted = img_array * brightness
    adjusted = np.clip(adjusted, 0, 255)
    adjusted = (adjusted - 128) * contrast + 128
    return Image.fromarray(np.clip(adjusted, 0, 255).astype(np.uint8))

def main():
    st.set_page_config(layout="wide")

    # 上传图片
    uploaded_file = st.file_uploader("Uploading a Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # 创建两列布局，图片占60%，编辑器占40%
        col1, col2 = st.columns([6, 4], gap="small")
        
        # 加载原始图片
        image = Image.open(uploaded_file)
        
        # 应用编辑并显示图片在左侧列
        with col1:
            # 计算缩小后的尺寸
            width, height = image.size
            new_width = int(width * 0.75)  # 使用原始宽度的75%
            new_height = int(height * (new_width / width))
            
            # 缩小图片
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # 显示缩小后的图片
            img_display = st.image(resized_image, use_column_width=True)

        with col2:
            st.subheader("Image Editor")
            
            # 获取显示图片的实际高度
            img_height = new_height
            
            # 计算编辑器组件的高度，使用图片显示的实际高度
            editor_height = int(img_height * 0.9)  # 使用90%的图像显示高度作为编辑器高度
            
            # 使用容器来组织编辑器控件，并设置高度
            with st.container():
                # 创建一个垂直布局的列
                col = st.container()
                
                # 在列中添加编辑器控件
                with col:
                    # 调整亮度
                    brightness = st.slider("亮度", 0.0, 2.0, 1.0, step=0.1)
                    
                    # 调整对比度
                    contrast = st.slider("对比度", 0.5, 1.5, 1.0, step=0.1)
                    
                    # 下载编辑后的图片
                    edited_image = adjust_image(image, brightness, contrast)
                    buf = io.BytesIO()
                    edited_image.save(buf, format="PNG")
                    st.download_button(
                        label="Download",
                        data=buf.getvalue(),
                        file_name="edited_image.png",
                        mime="image/png"
                    )
                
                # 使用自定义CSS来设置容器高度
                st.markdown(f"""
                    <style>
                        div.stContainer > div {{
                            max-height: {editor_height}px;
                            overflow-y: auto;
                        }}
                        .main .block-container {{
                            padding-top: 1rem;
                            padding-bottom: 1rem;
                            max-width: 100%;
                        }}
                        .stApp {{
                            max-width: 100%;
                        }}
                    </style>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()