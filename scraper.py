from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import os

class ProductScraper:
    def __init__(self, url):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Simple initialization with default settings
        service = Service()
        self.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        self.url = url
        # Set page load timeout to 30 seconds
        self.driver.set_page_load_timeout(30)
    
    def get_domain(self):
        """Extract domain from URL"""
        return urlparse(self.url).netloc
    
    def find_selectors(self):
        """Find and return selectors for product elements"""
        try:
            self.driver.get(self.url)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            selectors = {
                "product_name": self._find_product_name(soup),
                "price": self._find_price(soup),
                "sku": self._find_sku(soup),
                "quantity": self._find_quantity(soup),
                "quantity_up": self._find_quantity_buttons(soup, "up"),
                "quantity_down": self._find_quantity_buttons(soup, "down"),
                "add_to_cart": self._find_add_to_cart(soup)
            }
            
            return selectors
            
        finally:
            self.driver.quit()
    
    def _get_selector(self, element):
        """Generate CSS selector for an element"""
        if not element:
            return None
            
        # Try to find id
        if element.get('id'):
            return f"#{element['id']}"
            
        # Try to find unique class
        classes = element.get('class', [])
        for cls in classes:
            if cls and not cls.isspace():
                return f".{cls}"
        
        # Generate path as fallback
        path = []
        for parent in element.parents:
            if parent.name == '[document]':
                break
            if parent.get('id'):
                path.append(f"#{parent['id']}")
                break
            siblings = parent.find_previous_siblings(parent.name)
            path.append(f"{parent.name}:nth-child({len(siblings) + 1})")
        return ' > '.join(reversed(path))
    
    def _find_product_name(self, soup):
        """Find product name selector"""
        candidates = [
            soup.find('h1'),  # Most common for product titles
            soup.find(class_=re.compile(r'product.*title', re.I)),
            soup.find(class_=re.compile(r'product.*name', re.I))
        ]
        
        for candidate in candidates:
            if candidate:
                return self._get_selector(candidate)
        return None
    
    def _find_price(self, soup):
        """Find price selector"""
        price_patterns = [
            re.compile(r'price', re.I),
            re.compile(r'amount', re.I)
        ]
        
        for pattern in price_patterns:
            element = soup.find(class_=pattern)
            if element:
                return self._get_selector(element)
        return None
    
    def _find_sku(self, soup):
        """Find SKU selector"""
        sku_patterns = [
            re.compile(r'sku', re.I),
            re.compile(r'product.*code', re.I),
            re.compile(r'item.*number', re.I)
        ]
        
        for pattern in sku_patterns:
            element = soup.find(class_=pattern)
            if element:
                return self._get_selector(element)
        return None
    
    def _find_quantity(self, soup):
        """Find quantity input selector"""
        qty_patterns = [
            re.compile(r'quantity', re.I),
            re.compile(r'qty', re.I)
        ]
        
        for pattern in qty_patterns:
            element = soup.find('input', attrs={'name': pattern})
            if element:
                return self._get_selector(element)
        return None
    
    def _find_quantity_buttons(self, soup, direction):
        """Find quantity adjustment buttons"""
        patterns = [
            re.compile(f'{direction}', re.I),
            re.compile(f'quantity.*{direction}', re.I),
            re.compile(f'qty.*{direction}', re.I)
        ]
        
        for pattern in patterns:
            element = soup.find('button', class_=pattern)
            if element:
                return self._get_selector(element)
        return None
    
    def _find_add_to_cart(self, soup):
        """Find add to cart button selector"""
        cart_patterns = [
            re.compile(r'add.*cart', re.I),
            re.compile(r'buy.*now', re.I),
            re.compile(r'purchase', re.I)
        ]
        
        for pattern in cart_patterns:
            element = soup.find('button', class_=pattern) or soup.find('a', class_=pattern)
            if element:
                return self._get_selector(element)
        return None 