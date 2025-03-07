import streamlit as st
from scraper import ProductScraper
import validators

def main():
    st.title("E-commerce Product Page Selector Finder")
    
    # URL input
    url = st.text_input("Enter product page URL:")
    
    if url and not validators.url(url):
        st.error("Please enter a valid URL")
        return
    
    # Initialize scraper
    if url:
        try:
            scraper = ProductScraper(url)
            
            if st.button("Find Selectors"):
                with st.spinner("Analyzing page..."):
                    selectors = scraper.find_selectors()
                    
                    # Display results in a more readable format
                    st.subheader("Found Selectors")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Product Details")
                        st.text("Product Name:")
                        st.code(selectors["product_name"] or "Not found")
                        st.text("Price:")
                        st.code(selectors["price"] or "Not found")
                        st.text("SKU:")
                        st.code(selectors["sku"] or "Not found")
                    
                    with col2:
                        st.markdown("#### Purchase Controls")
                        st.text("Quantity Input:")
                        st.code(selectors["quantity"] or "Not found")
                        st.text("Quantity Up Button:")
                        st.code(selectors["quantity_up"] or "Not found")
                        st.text("Quantity Down Button:")
                        st.code(selectors["quantity_down"] or "Not found")
                        st.text("Add to Cart Button:")
                        st.code(selectors["add_to_cart"] or "Not found")
                    
                    # Display domain info
                    st.info(f"Domain analyzed: {scraper.get_domain()}")
                    
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 