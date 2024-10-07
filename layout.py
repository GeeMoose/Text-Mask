import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import json
import sseclient

def add_text_to_image(image, text, font_size, text_color):
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(font="./fonts/ABeeZee_italic_400.ttf", size=font_size)
    except IOError:
        print("font not found")
        # 如果默认字体不可用，使用默认位图字体
        font = ImageFont.load_default()
    # 使用font.getbbox()方法获取文本边界框
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    # 计算文字在图片中心正上方的位置
    x = (image.width - text_width) / 2
    y = 10

    position = (x, y)

    draw.text(position, text, font=font, fill=text_color)
    return image

def main():
    st.set_page_config(layout="wide")

    # 上传图片
    uploaded_file = st.file_uploader("Uploading a Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer 1234'
        }
        files = {'file': (file_name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(
            f'https://a1d-rb.k-xshar.workers.dev/api/uploads/{file_name}', headers=headers, files=files)
        # 创建两列布局，图片占60%，编辑器占40%
        col1, col2 = st.columns([6, 4], gap="small")
        
        # 加载原始图片
        image = Image.open(uploaded_file)
        # 生成和处理前景图
        fore_headers = {
             "Content-Type": "application/json",
             'accept': 'application/json',
             'Authorization': 'Bearer 1234'
        }
        res = requests.post(f'https://a1d-rb.k-xshar.workers.dev/api/task', headers=fore_headers, json={"image_url": response.json().get('url')})
        id = res.json().get('id')
        try:
            response = requests.get(f'https://a1d-rb.k-xshar.workers.dev/api/task/{id}/sse', headers={
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
            }, stream=True)
            try:
                client = sseclient.SSEClient(response)
            except Exception as e:
                print(f"Create SSEClient error: {str(e)}")
                client = None
            
            fore_image_url = None
            fore_image = None
            for event in client.events():
                if event.data:
                    try:
                        data = json.loads(event.data)
                        if data.get('status') == 'FINISHED':
                            fore_image_url = data.get('image_url')
                            break

                    except json.JSONDecodeError:
                        print("error")  
                else:
                    print("error")
            
            # 将URL转换为streamlit.Image可读取的文件形式
            if fore_image_url:
                response = requests.get(fore_image_url)
                if response.status_code == 200:
                    image_bytes = response.content
                    fore_image = Image.open(io.BytesIO(image_bytes))

        except:
            print("error")
        
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
                    text_input = st.text_input("Text")
                    font_size = st.slider("Font Size", 10, 100, 70)
                    text_color = st.color_picker("Text Color", "#000000")
                    if text_input:
                        edited_image = add_text_to_image(image, text_input, font_size, text_color)
                        # Load fore image
                        if fore_image:
                            # 将前景图调整为与编辑后图像相同的大小
                            fore_image = fore_image.resize(edited_image.size, Image.LANCZOS)
                            
                            # 确保编辑后的图像为RGBA模式
                            edited_image = edited_image.convert('RGBA')
                            
                            # 创建一个与编辑后图像相同大小的透明图层
                            overlay = Image.new('RGBA', edited_image.size, (255, 255, 255, 0))
                            
                            # 将前景图粘贴到透明图层上
                            overlay.paste(fore_image, (0, 0), fore_image)
                        
                            # 将透明图层与编辑后的图像合成
                            edited_image = Image.alpha_composite(edited_image, overlay)
                    else:
                        edited_image = image
                    
                    img_display.image(edited_image, use_column_width=True)
                    
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