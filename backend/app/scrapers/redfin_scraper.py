#!/usr/bin/env python3
import os
import csv
import time
import re
import random
import logging
from shutil import which
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
import argparse

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class RedfinScraper(BaseScraper):
    """
    Builds a Redfin URL with optional filters and scrapes listings with Firefox + Selenium.

    Filters:
      - min_price, max_price: int (dollars), e.g., 100000 -> "100k"
      - min_beds, max_beds: int
      - min_baths: float
      - property_types: list[str], e.g., ["house", "multifamily"]
      - location_path: Redfin path for the area
          default: "city/15702/PA/Pittsburgh"
    """
    
    # Redfin location paths for common cities
    LOCATION_MAP = {
        'pittsburgh_pa': 'city/15702/PA/Pittsburgh',
        'philadelphia_pa': 'city/13271/PA/Philadelphia',
        'new-york_ny': 'city/30749/NY/New-York',
        'boston_ma': 'city/1826/MA/Boston',
        'chicago_il': 'city/29470/IL/Chicago',
        'los-angeles_ca': 'city/11203/CA/Los-Angeles',
        'san-francisco_ca': 'city/17151/CA/San-Francisco',
        'seattle_wa': 'city/16163/WA/Seattle',
        'austin_tx': 'city/30818/TX/Austin',
        'denver_co': 'city/13059/CO/Denver',
    }

    def __init__(
        self,
        location_path: str = "city/15702/PA/Pittsburgh",
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_beds: Optional[int] = None,
        max_beds: Optional[int] = None,
        min_baths: Optional[float] = None,
        property_types: Optional[List[str]] = None,
        headless: bool = False,
        csv_filename: str = "redfin_listings.csv",
        download_dir: Optional[str] = None,
        rate_limit: float = 3.0,
    ):
        super().__init__(rate_limit)
        self.location_path = location_path
        self.min_price = min_price
        self.max_price = max_price
        self.min_beds = min_beds
        self.max_beds = max_beds
        self.min_baths = min_baths
        self.property_types = property_types or []
        self.headless = headless

        # Output CSV next to this script (unless user gives an absolute path)
        if os.path.isabs(csv_filename):
            self.csv_filename = csv_filename
        else:
            self.csv_filename = os.path.join(SCRIPT_DIR, csv_filename)

        # Download directory next to this script by default
        if download_dir is None:
            self.download_dir = os.path.join(SCRIPT_DIR, "redfin_downloads")
        else:
            self.download_dir = os.path.abspath(download_dir)
    
    def get_source_name(self) -> str:
        return "redfin"
    
    @classmethod
    def _get_location_path(cls, city: str, state: str) -> str:
        """Get the Redfin location path for a city/state"""
        # Normalize city name
        city_key = f"{city.lower().replace(' ', '-')}_{state.lower()}"
        
        if city_key in cls.LOCATION_MAP:
            return cls.LOCATION_MAP[city_key]
        
        # Fallback: use Pittsburgh as default
        logger.warning(f"No Redfin location path for {city}, {state}. Using Pittsburgh as fallback.")
        return cls.LOCATION_MAP['pittsburgh_pa']
    
    def search_properties(
        self,
        city: str,
        state: str,
        max_price: Optional[int] = None,
        min_beds: Optional[int] = None,
        min_baths: Optional[float] = None,
        property_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for properties on Redfin"""
        logger.info(f"Scraping Redfin for properties in {city}, {state}")
        
        try:
            # Get location path
            location_path = self._get_location_path(city, state)
            
            # Map property type to Redfin types
            property_types = None
            if property_type:
                type_map = {
                    'house': ['house'],
                    'condo': ['condo'],
                    'townhouse': ['townhouse'],
                }
                property_types = type_map.get(property_type.lower())
            
            # Update scraper config for this search
            self.location_path = location_path
            self.max_price = max_price
            self.min_beds = min_beds
            self.min_baths = min_baths
            self.property_types = property_types
            
            # Scrape the first page only (to avoid long-running scrapes)
            logger.info("Scraping first 3 pages of Redfin results...")
            listings = self.scrape(pages="3")
            
            # Convert to our standard format
            properties = []
            for listing in listings:
                try:
                    prop = self._convert_redfin_listing(listing, city, state)
                    if prop:
                        properties.append(prop)
                except Exception as e:
                    logger.error(f"Error converting Redfin listing: {e}")
                    continue
            
            logger.info(f"Found {len(properties)} properties on Redfin")
            return properties
            
        except Exception as e:
            logger.error(f"Error scraping Redfin: {e}")
            return []
    
    def _convert_redfin_listing(self, listing: Dict, city: str, state: str) -> Optional[Dict]:
        """Convert a Redfin listing to our standard format"""
        try:
            # Parse price
            price_str = listing.get('price', '').replace('$', '').replace(',', '').strip()
            if not price_str or price_str == '—':
                return None
            
            # Handle price ranges (e.g., "$200K-$250K")
            if '-' in price_str:
                price_str = price_str.split('-')[0]
            
            # Handle K/M suffixes
            if 'K' in price_str.upper():
                price = float(price_str.upper().replace('K', '')) * 1000
            elif 'M' in price_str.upper():
                price = float(price_str.upper().replace('M', '')) * 1000000
            else:
                price = float(price_str)
            
            # Parse beds
            beds_str = listing.get('beds', '').strip()
            beds = 0
            if beds_str and beds_str != '—':
                beds_match = re.search(r'(\d+)', beds_str)
                if beds_match:
                    beds = int(beds_match.group(1))
            
            # Parse baths
            baths_str = listing.get('baths', '').strip()
            baths = 0.0
            if baths_str and baths_str != '—':
                baths_match = re.search(r'([\d.]+)', baths_str)
                if baths_match:
                    baths = float(baths_match.group(1))
            
            # Parse sqft
            sqft_str = listing.get('area', '').replace(',', '').strip()
            sqft = 0
            if sqft_str and sqft_str != '—':
                sqft_match = re.search(r'(\d+)', sqft_str)
                if sqft_match:
                    sqft = int(sqft_match.group(1))
            
            # Parse address
            address_full = listing.get('address', '').strip()
            address_parts = address_full.split(',')
            street = address_parts[0].strip() if address_parts else address_full
            
            # Try to extract zip from address
            zip_code = ""
            zip_match = re.search(r'\b(\d{5})\b', address_full)
            if zip_match:
                zip_code = zip_match.group(1)
            
            # Listing URL
            listing_url = listing.get('url', '')
            
            # Image URL
            image_url = listing.get('image_url', '')
            
            # Determine property type from URL or default to house
            prop_type = 'house'
            if listing_url:
                if '/condo/' in listing_url:
                    prop_type = 'condo'
                elif '/townhouse/' in listing_url:
                    prop_type = 'townhouse'
            
            raw_data = {
                'address': street,
                'city': city,
                'state': state.upper(),
                'zip_code': zip_code,
                'price': price,
                'beds': beds,
                'baths': baths,
                'sqft': sqft,
                'property_type': prop_type,
                'listing_url': listing_url,
                'image_url': image_url
            }
            
            return self._normalize_property(raw_data)
            
        except Exception as e:
            logger.error(f"Error parsing Redfin listing: {e}")
            return None

    # ---------- Browser setup ----------

    def create_driver(self) -> webdriver.Firefox:
        """
        Create a Firefox WebDriver using the snap-safe setup,
        plus auto-download of CSV files to a known directory.
        """
        # Temp dir fix for snap Firefox
        tmpdir = os.path.expanduser("~/geckotmp")
        os.makedirs(tmpdir, exist_ok=True)
        os.environ["TMPDIR"] = tmpdir

        options = FirefoxOptions()
        if self.headless:
            options.add_argument("-headless")

        firefox_bin = which("firefox")
        if firefox_bin:
            options.binary_location = firefox_bin

        # Download directory for CSVs (next to this script)
        os.makedirs(self.download_dir, exist_ok=True)
        options.set_preference("browser.download.folderList", 2)  # 2 = use custom dir
        options.set_preference("browser.download.dir", self.download_dir)
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "text/csv,application/csv,application/octet-stream",
        )

        gecko_path = GeckoDriverManager().install()
        service = FirefoxService(executable_path=gecko_path)

        driver = webdriver.Firefox(service=service, options=options)
        driver.set_window_size(1400, 900)
        return driver

    # ---------- URL building helpers ----------

    @staticmethod
    def _format_price(value: int) -> str:
        """Convert numeric price to Redfin format"""
        if value >= 1000 and value % 1000 == 0:
            return f"{value // 1000}k"
        return str(value)

    def build_base_url(self) -> str:
        """Build the base Redfin URL including filters"""
        base = f"https://www.redfin.com/{self.location_path}"
        filter_parts: List[str] = []

        # property types
        if self.property_types:
            types_str = "+".join(
                t.strip().lower() for t in self.property_types if t.strip()
            )
            if types_str:
                filter_parts.append(f"property-type={types_str}")

        # price range
        if self.min_price is not None:
            filter_parts.append(f"min-price={self._format_price(self.min_price)}")
        if self.max_price is not None:
            filter_parts.append(f"max-price={self._format_price(self.max_price)}")

        # beds
        if self.min_beds is not None:
            filter_parts.append(f"min-beds={self.min_beds}")
        if self.max_beds is not None:
            filter_parts.append(f"max-beds={self.max_beds}")

        # baths
        if self.min_baths is not None:
            filter_parts.append(f"min-baths={self.min_baths}")

        if filter_parts:
            return base + "/filter/" + ",".join(filter_parts)
        else:
            return base

    # ---------- Page interaction helpers ----------

    def _scroll_to_bottom(self, driver: webdriver.Firefox, pause: float = 0.3, step: int = 400):
        """
        Smoothly scroll down until the pagination section (Next button) is in view.
        This is more demo-friendly than jumping straight to the bottom.
        """

        try:
            pagination = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button.PageArrow__direction--next")
                )
            )
        except TimeoutException:
            # Fallback: smooth scroll to bottom if no pagination appears
            last_height = driver.execute_script("return document.body.scrollHeight")
            current_pos = 0
            while current_pos < last_height:
                driver.execute_script(f"window.scrollTo(0, {current_pos});")
                time.sleep(pause + random.uniform(0.0, 0.2))
                current_pos += step
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height <= last_height:
                    break
                last_height = new_height
            return

        # Smooth scroll until the pagination section is visible in the viewport
        while True:
            in_view = driver.execute_script(
                """
                const elem = arguments[0];
                const rect = elem.getBoundingClientRect();
                const vh = window.innerHeight || document.documentElement.clientHeight;
                return rect.top >= 0 && rect.top < vh;
                """,
                pagination,
            )

            if in_view:
                break

            driver.execute_script(f"window.scrollBy(0, {step});")
            time.sleep(pause + random.uniform(0.0, 0.2))

            at_bottom = driver.execute_script(
                "return (window.innerHeight + window.scrollY) >= document.body.scrollHeight;"
            )
            if at_bottom:
                break

    def _parse_listing_cards(self, driver: webdriver.Firefox) -> List[Dict]:
        """
        Extract data from Redfin listing cards on the current page.

        Uses the HomeCardContainer / MapHomeCard_* structure.
        """
        listings: List[Dict] = []

        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "div.HomeCardContainer[id^='MapHomeCard_']"
        )

        for card in cards:
            try:
                # Price
                price = ""
                try:
                    price_el = card.find_element(By.CSS_SELECTOR, "span.bp-Homecard__Price--value")
                    price = price_el.text.strip()
                except Exception:
                    pass

                beds = baths = area = ""

                try:
                    beds_el = card.find_element(By.CSS_SELECTOR, "span.bp-Homecard__Stats--beds")
                    beds = beds_el.text.strip()
                except Exception:
                    pass

                try:
                    baths_el = card.find_element(By.CSS_SELECTOR, "span.bp-Homecard__Stats--baths")
                    baths = baths_el.text.strip()
                except Exception:
                    pass

                try:
                    sqft_val_el = card.find_element(
                        By.CSS_SELECTOR,
                        "span.bp-Homecard__Stats--sqft span.bp-Homecard__LockedStat--value"
                    )
                    area = sqft_val_el.text.strip()
                except Exception:
                    pass

                address = ""
                url = ""
                try:
                    addr_el = card.find_element(By.CSS_SELECTOR, "a.bp-Homecard__Address")
                    address = addr_el.text.strip()
                    url = addr_el.get_attribute("href") or ""
                except Exception:
                    pass

                image_url = ""
                try:
                    img_el = card.find_element(By.CSS_SELECTOR, "img.bp-Homecard__Photo--image")
                    image_url = img_el.get_attribute("src") or ""
                except Exception:
                    pass

                if not (price or address):
                    continue

                listings.append(
                    {
                        "price": price,
                        "address": address,
                        "beds": beds,
                        "baths": baths,
                        "area": area,
                        "url": url,
                        "image_url": image_url,
                    }
                )

            except Exception:
                continue

        return listings

    def _go_to_next_page(self, driver: webdriver.Firefox) -> bool:
        """
        Click Redfin's 'Next' pagination button if it exists.
        Returns True if we navigated, False if no more pages.
        """
        try:
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.PageArrow__direction--next")
                )
            )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(0.5)

            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2.0)
            return True

        except TimeoutException:
            return False
        except Exception:
            return False

    def _get_max_pages(self, driver: webdriver.Firefox) -> int:
        """
        Parse the "Viewing page 1 of 9" text to determine the total number of pages.
        Falls back to 1 if it can't be found/parsed.
        """
        try:
            span = driver.find_element(
                By.CSS_SELECTOR,
                "span.pageText[data-rf-test-name='download-and-save-page-number-text']",
            )
            txt = span.text.strip()  # e.g. "Viewing page 1 of 9"
            m = re.search(r"of\s+(\d+)", txt)
            if m:
                return int(m.group(1))
        except Exception:
            pass
        return 1

    # ---------- Redfin "Download All" CSV helpers ----------

    def _wait_for_csv(self, timeout: int = 60) -> Optional[str]:
        """Wait for a CSV file to appear in the download directory"""
        download_dir = self.download_dir
        end = time.time() + timeout

        while time.time() < end:
            csv_files = [
                f for f in os.listdir(download_dir)
                if f.lower().endswith(".csv")
            ]
            if csv_files:
                csv_files.sort(
                    key=lambda f: os.path.getmtime(os.path.join(download_dir, f)),
                    reverse=True,
                )
                latest = os.path.join(download_dir, csv_files[0])
                return latest

            time.sleep(1)

        return None

    def _parse_download_row(self, row: Dict[str, str]) -> Dict:
        """Convert a Redfin CSV row into our internal format"""
        if "In accordance with local MLS rules" in row.get("SALE TYPE", ""):
            return {}

        def clean_int(value: str) -> Optional[int]:
            value = (value or "").replace(",", "").strip()
            if not value:
                return None
            try:
                return int(float(value))
            except ValueError:
                return None

        def clean_float(value: str) -> Optional[float]:
            value = (value or "").replace(",", "").strip()
            if not value:
                return None
            try:
                return float(value)
            except ValueError:
                return None

        price = clean_int(row.get("PRICE", ""))
        beds = clean_float(row.get("BEDS", ""))
        baths = clean_float(row.get("BATHS", ""))
        sqft = clean_int(row.get("SQUARE FEET", ""))

        address_parts = [
            row.get("ADDRESS", "").strip(),
            row.get("CITY", "").strip(),
            row.get("STATE OR PROVINCE", "").strip(),
            row.get("ZIP OR POSTAL CODE", "").strip(),
        ]
        address = ", ".join(p for p in address_parts if p)

        url = (
            row.get(
                "URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)",
                "",
            )
            or ""
        ).strip()

        lat = clean_float(row.get("LATITUDE", ""))
        lng = clean_float(row.get("LONGITUDE", ""))

        return {
            "price": price,
            "address": address,
            "beds": beds,
            "baths": baths,
            "area": sqft,
            "url": url,
            "lat": lat,
            "lng": lng,
            "raw": row,
        }

    def load_download_csv(self, path: str) -> List[Dict]:
        """Load listings from a Redfin CSV export"""
        listings: List[Dict] = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                parsed = self._parse_download_row(row)
                if parsed:
                    listings.append(parsed)

        return listings

    def download_and_load_csv(self) -> List[Dict]:
        """Open Redfin, download CSV, and parse listings"""
        driver = self.create_driver()
        base_url = self.build_base_url()

        try:
            driver.get(base_url)

            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.HomeCardContainer[id^='MapHomeCard_']")
                    )
                )
            except TimeoutException:
                pass

            input("Press ENTER when ready to download CSV... ")

            # Locate and click the Download All link
            try:
                download_span = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "#download-and-save span.clickable")
                    )
                )
            except TimeoutException:
                download_span = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "#download-and-save")
                    )
                )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_span)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", download_span)

            csv_path = self._wait_for_csv(timeout=60)
            if not csv_path:
                return []

            listings = self.load_download_csv(csv_path)
            return listings

        finally:
            driver.quit()

    # ---------- Main scraping (card-based) ----------

    def scrape(self, pages: str = "1") -> List[Dict]:
        """Scrape listings from Redfin"""
        driver = self.create_driver()
        all_listings: List[Dict] = []

        base_url = self.build_base_url()

        try:
            driver.get(base_url)

            WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.HomeCardContainer[id^='MapHomeCard_']")
                )
            )

            max_pages_available = self._get_max_pages(driver)

            if pages == "max":
                total_pages = max_pages_available
            else:
                requested = int(pages)
                total_pages = min(requested, max_pages_available)

            for page_num in range(1, total_pages + 1):
                self._scroll_to_bottom(driver)

                page_listings = self._parse_listing_cards(driver)

                all_listings.extend(page_listings)

                if page_num < total_pages:
                    has_next = self._go_to_next_page(driver)
                    if not has_next:
                        break

                    WebDriverWait(driver, 60).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "div.HomeCardContainer[id^='MapHomeCard_']")
                        )
                    )

        finally:
            driver.quit()

        return all_listings

    # ---------- CSV output ----------

    def save_to_csv(self, listings: List[Dict]):
        if not listings:
            return

        all_keys = set()
        for row in listings:
            all_keys.update(row.keys())
        preferred_order = ["price", "address", "beds", "baths", "area", "url", "lat", "lng"]
        fieldnames = [k for k in preferred_order if k in all_keys] + [
            k for k in sorted(all_keys) if k not in preferred_order
        ]

        os.makedirs(os.path.dirname(self.csv_filename), exist_ok=True)

        with open(self.csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in listings:
                writer.writerow(row)
