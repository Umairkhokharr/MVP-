import streamlit as st
from PIL import Image
import base64
import io
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="MerchSentAI",
    layout="centered",
    page_icon="🛍️"
)

# Function to load image from base64
def load_base64_image(b64_string):
    try:
        if b64_string.startswith('data:image'):
            image_data = base64.b64decode(b64_string.split(',')[1])
        else:
            image_data = base64.b64decode(b64_string)
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# Main app function
def main():
    # App header
    st.title("🛍️ MerchSentAI")
    st.markdown("### AI-powered Merchandise Sentiment Analysis")
    
    # Image processing section
    with st.expander("🖼️ Image Processing", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upload Image")
            uploaded_file = st.file_uploader("Choose merchandise image", type=["jpg", "jpeg", "png"])
            
            if uploaded_file:
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                    st.success("✅ Image processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col2:
            st.subheader("Base64 Image Input")
            base64_input = st.text_area("Paste base64 string:", height=150)
            
            if st.button("Decode Base64") and base64_input:
                with st.spinner("Decoding..."):
                    decoded_image = load_base64_image(base64_input)
                    if decoded_image:
                        st.image(decoded_image, caption="Decoded Image", use_column_width=True)
                        st.success("✅ Image decoded successfully!")
    
    # Sentiment analysis section
    st.header("😊 Sentiment Analysis")
    user_input = st.text_area("Enter customer feedback:", placeholder="The product quality was excellent but delivery was slow...", height=100)
    
    if st.button("Analyze Sentiment") and user_input:
        with st.spinner("Analyzing..."):
            # Mock analysis - replace with your real model
            positive_score = min(len(user_input)/100, 0.95)
            negative_score = 1 - positive_score
            
            # Display results
            st.subheader("Analysis Results")
            col1, col2 = st.columns(2)
            col1.metric("Positive", f"{positive_score*100:.1f}%", delta="+12% from avg")
            col2.metric("Negative", f"{negative_score*100:.1f}%", delta="-3% from avg")
            
            # Visual indicator
            st.progress(positive_score)
            
            # Sample insights
            st.info("💡 Detected keywords: quality, excellent, delivery")
            if positive_score > 0.7:
                st.success("🌟 Excellent feedback! Customers love your merchandise.")
            else:
                st.warning("⚠️ Mixed feedback detected. Consider improving delivery times.")
    
    # Excel analysis section
    st.header("📊 Excel Data Analysis")
    uploaded_excel = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
    
    if uploaded_excel:
        try:
            df = pd.read_excel(uploaded_excel)
            st.success("✅ File loaded successfully!")
            
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            st.subheader("Basic Statistics")
            st.write(df.describe())
            
            # Add your custom analysis here
            if 'rating' in df.columns:
                st.subheader("Rating Distribution")
                st.bar_chart(df['rating'].value_counts())
                
        except Exception as e:
            st.error(f"❌ Error processing Excel file: {e}")

# Run the app
if __name__ == "__main__":
    main()