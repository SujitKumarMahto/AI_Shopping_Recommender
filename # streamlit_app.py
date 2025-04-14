import streamlit as st
import requests

st.set_page_config(page_title="Shopping Recommender", page_icon="🛍️")

st.title("🛍️ Personalized Shopping Recommender System")

# Since user IDs are like CUST00001, use text input instead of number
user_id = st.text_input("Enter User ID (e.g., CUST00001)")

if st.button("Get Recommendations"):
    if user_id.strip() == "":
        st.warning("Please enter a valid User ID.")
    else:
        try:
            # Send GET request to Flask app
            response = requests.get(f"http://127.0.0.1:5000/recommend?user_id={user_id}")
            
            if response.status_code == 200:
                # Get the recommendations from Flask response
                recommendations = response.json()["recommendations"]
                st.success("Top Recommendations:")
                
                for rec in recommendations:
                    st.markdown(f"🛒 **Product ID:** `{rec['product_id']}` | ⭐ **Estimated Score:** `{rec['estimated_score']:.2f}`")
            else:
                try:
                    error_msg = response.json().get("error", "Unknown error occurred.")
                except:
                    error_msg = "Unknown error occurred."
                st.error(f"❌ {error_msg}")
        
        except Exception as e:
            st.error(f"🚨 Error: {e}")