import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from urllib.parse import urljoin

class FlipkartReviewScraper:
    def __init__(self):
        self.session = requests.Session()
        # Add headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def parse_reviews(self, html_content):
        """Parse reviews from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        reviews = []
        
        # Find all review containers - in my case, reviews are in div elements
        # Try multiple selectors to catch the review containers
        review_containers = soup.find_all('div', {'class': lambda x: x and ('col/div name' in x or 'review' in x.lower())})
        
        # If the above doesn't work, try finding by common review patterns
        if not review_containers:
            review_containers = soup.find_all('div', string=lambda text: text and ('★' in text or 'star' in text.lower()))
            review_containers = [container.find_parent('div') for container in review_containers if container.find_parent('div')]
        
        for container in review_containers:
            try:
                review_data = {}
                
                # Extract rating (look for star ratings)
                rating_elem = container.find('div', {'class': lambda x: x and 'star' in x.lower()}) or \
                            container.find(string=lambda text: text and '★' in text)
                if rating_elem:
                    if isinstance(rating_elem, str):
                        # Count stars in the string
                        review_data['rating'] = rating_elem.count('★')
                    else:
                        rating_text = rating_elem.get_text()
                        if '★' in rating_text:
                            review_data['rating'] = rating_text.count('★')
                        else:
                            # Try to extract numeric rating
                            import re
                            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                            if rating_match:
                                review_data['rating'] = float(rating_match.group(1))
                
                # Extract review title
                title_elem = container.find('p', {'class': lambda x: x and ('title' in x or 'heading' in x)})
                if title_elem:
                    review_data['title'] = title_elem.get_text().strip()
                
                # Extract review text - look for longer text content
                text_elements = container.find_all('div', string=lambda text: text and len(text.strip()) > 20)
                if text_elements:
                    review_data['review_text'] = text_elements[0].get_text().strip()
                
                # Extract reviewer name
                name_elem = container.find('p', {'class': lambda x: x and 'name' in x.lower()}) or \
                           container.find('span', {'class': lambda x: x and 'name' in x.lower()})
                if name_elem:
                    review_data['reviewer_name'] = name_elem.get_text().strip()
                
                # Extract date
                date_elem = container.find(string=lambda text: text and any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']))
                if date_elem:
                    review_data['date'] = date_elem.strip()
                
                # Extract helpful votes
                helpful_elem = container.find(string=lambda text: text and 'helpful' in text.lower())
                if helpful_elem:
                    import re
                    helpful_match = re.search(r'(\d+)', helpful_elem)
                    if helpful_match:
                        review_data['helpful_votes'] = int(helpful_match.group(1))
                
                # Only add review if we got some meaningful data
                if any(key in review_data for key in ['rating', 'review_text', 'title']):
                    reviews.append(review_data)
                    
            except Exception as e:
                print(f"Error parsing review: {e}")
                continue
        
        return reviews
    
    def scrape_reviews(self, base_url, max_pages=5):
        """Scrape reviews from multiple pages"""
        all_reviews = []
        
        for page in range(1, max_pages + 1):
            if page == 1:
                url = base_url
            else:
                # Add page parameter to URL
                if '?' in base_url:
                    url = f"{base_url}&page={page}"
                else:
                    url = f"{base_url}?page={page}"
            
            print(f"Scraping page {page}: {url}")
            
            html_content = self.get_page_content(url)
            if not html_content:
                print(f"Failed to fetch page {page}")
                continue
            
            reviews = self.parse_reviews(html_content)
            if not reviews:
                print(f"No reviews found on page {page}")
                # If we get no reviews, we might have reached the end
                if page > 1:
                    break
            else:
                all_reviews.extend(reviews)
                print(f"Found {len(reviews)} reviews on page {page}")
            
            # Be respectful with delays
            time.sleep(2)
        
        return all_reviews
    
    def save_to_csv(self, reviews, filename='flipkart_reviews.csv'):
        """Save reviews to CSV file"""
        if not reviews:
            print("No reviews to save")
            return
        
        fieldnames = ['rating', 'title', 'review_text', 'reviewer_name', 'date', 'helpful_votes']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for review in reviews:
                writer.writerow(review)
        
        print(f"Saved {len(reviews)} reviews to {filename}")
    
    def save_to_json(self, reviews, filename='flipkart_reviews.json'):
        """Save reviews to JSON file"""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(reviews, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(reviews)} reviews to {filename}")

# Usage example
if __name__ == "__main__":
    # Your review page URL
    review_url = "https://www.flipkart.com/something/something/as you need "
    
    # Create scraper instance
    scraper = FlipkartReviewScraper()
    
    # Scrape reviews (adjust max_pages as needed)
    reviews = scraper.scrape_reviews(review_url, max_pages=5)
    
    # Display results
    print(f"\nTotal reviews scraped: {len(reviews)}")
    
    # Show first few reviews as sample
    for i, review in enumerate(reviews[:3]):
        print(f"\nReview {i+1}:")
        for key, value in review.items():
            print(f"  {key}: {value}")
    
    # Save to files
    if reviews:
        scraper.save_to_csv(reviews)
        scraper.save_to_json(reviews)
    
    print("Scraping completed!")
