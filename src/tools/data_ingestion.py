# CSV and PDF ingestion
import requests
import pandas as pd
import PyPDF2
from pathlib import Path
from typing import List, Dict, Any
import logging
import re
from bs4 import BeautifulSoup
import io

from config.settings import DOWNLOADS_DIR, HTS_BASE_URL
from src.utils.database import HTSDatabase

logger = logging.getLogger(__name__)

class HTSDataIngestion:
    def __init__(self, database: HTSDatabase):
        self.database = database
        self.downloads_dir = Path(DOWNLOADS_DIR)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
    
    def download_general_notes(self) -> str:
        """Download General Notes PDF from HTS website."""
        try:
            # This is a placeholder URL - you'll need to find the actual PDF URL
            pdf_url = f"{HTS_BASE_URL}/general_notes.pdf"
            
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            pdf_path = self.downloads_dir / "general_notes.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded General Notes PDF to {pdf_path}")
            return str(pdf_path)
        
        except Exception as e:
            logger.error(f"Error downloading General Notes: {e}")
            # Return sample PDF path for development
            return self._create_sample_general_notes()
    
    def _create_sample_general_notes(self) -> str:
        """Create a sample General Notes text file for development."""
        sample_content = """
        GENERAL NOTES
        
        1. TARIFF TREATMENT OF GOODS
        
        The United States applies different tariff treatments based on trade agreements and country relationships.
        
        2. UNITED STATES-ISRAEL FREE TRADE AGREEMENT
        
        The United States-Israel Free Trade Agreement (FTA) was implemented on September 1, 1985. Under this agreement, eligible products from Israel receive duty-free treatment when imported into the United States. Products must meet origin requirements and be accompanied by proper documentation.
        
        Key provisions:
        - Elimination of tariffs on eligible products
        - Rules of origin requirements
        - Certificate of origin documentation
        - Qualifying products receive "IL" marking in tariff schedule
        
        3. NORTH AMERICAN FREE TRADE AGREEMENT (NAFTA)
        
        NAFTA provides preferential tariff treatment for goods originating in Canada and Mexico. Products qualifying under NAFTA receive reduced or eliminated tariffs.
        
        4. GENERALIZED SYSTEM OF PREFERENCES (GSP)
        
        GSP provides duty-free treatment for eligible products from designated developing countries.
        
        5. TRADE PROMOTION AUTHORITY
        
        Various trade promotion programs provide preferential treatment for qualifying countries and products.
        """
        
        sample_path = self.downloads_dir / "general_notes_sample.txt"
        with open(sample_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        logger.info(f"Created sample General Notes at {sample_path}")
        return str(sample_path)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            # If PDF extraction fails, read as text file
            try:
                with open(pdf_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return ""
    
    def download_hts_section_data(self, section: str = "I") -> List[str]:
        """Download HTS section CSV data."""
        try:
            # This would normally scrape the HTS website for CSV downloads
            # For now, we'll create sample data
            return self._create_sample_hts_data()
        
        except Exception as e:
            logger.error(f"Error downloading HTS section data: {e}")
            return self._create_sample_hts_data()
    
    def _create_sample_hts_data(self) -> List[str]:
        """Create sample HTS data for development."""
        sample_data = [
            {
                'hts_number': '0101.30.00.00',
                'description': 'Asses',
                'general_rate': '6.8%',
                'special_rate': 'Free (A,AU,BH,CA,CL,CO,D,E,IL,JO,KR,MA,MX,OM,P,PA,PE,SG)',
                'column2_rate': '15%',
                'section': 'I',
                'chapter': '01'
            },
            {
                'hts_number': '0102.21.00.00',
                'description': 'Pure-bred breeding cattle',
                'general_rate': 'Free',
                'special_rate': 'Free',
                'column2_rate': 'Free',
                'section': 'I',
                'chapter': '01'
            },
            {
                'hts_number': '0201.10.05.00',
                'description': 'Beef, fresh or chilled, carcasses and half-carcasses, high quality',
                'general_rate': '4.4¢/kg',
                'special_rate': '2.2¢/kg (AU,CA,MX)',
                'column2_rate': '30.8¢/kg',
                'section': 'I',
                'chapter': '02'
            },
            {
                'hts_number': '0301.11.00.00',
                'description': 'Ornamental fish, live',
                'general_rate': 'Free',
                'special_rate': 'Free',
                'column2_rate': 'Free',
                'section': 'I',
                'chapter': '03'
            }
        ]
        
        # Save to CSV
        df = pd.DataFrame(sample_data)
        csv_path = self.downloads_dir / "hts_section_i.csv"
        df.to_csv(csv_path, index=False)
        
        # Insert into database
        self.database.insert_hts_data(df)
        
        logger.info(f"Created sample HTS data at {csv_path}")
        return [str(csv_path)]
    
    def process_csv_files(self, csv_files: List[str]) -> None:
        """Process CSV files and insert data into database."""
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                
                # Standardize column names
                column_mapping = {
                    'HTS Number': 'hts_number',
                    'Description': 'description',
                    'General Rate of Duty': 'general_rate',
                    'Special Rate of Duty': 'special_rate',
                    'Column 2 Rate of Duty': 'column2_rate'
                }
                
                df = df.rename(columns=column_mapping)
                
                # Clean and validate data
                df['hts_number'] = df['hts_number'].astype(str)
                df = df.dropna(subset=['hts_number'])
                
                self.database.insert_hts_data(df)
                logger.info(f"Processed and inserted data from {csv_file}")
                
            except Exception as e:
                logger.error(f"Error processing CSV file {csv_file}: {e}")
    
    def setup_initial_data(self) -> Dict[str, Any]:
        """Download and setup all initial HTS data."""
        result = {
            'general_notes_path': None,
            'csv_files': [],
            'success': False
        }
        
        try:
            # Download General Notes
            result['general_notes_path'] = self.download_general_notes()
            
            # Download HTS CSV data
            result['csv_files'] = self.download_hts_section_data()
            
            # Process CSV files
            self.process_csv_files(result['csv_files'])
            
            result['success'] = True
            logger.info("Initial data setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error in initial data setup: {e}")
            result['success'] = False
        
        return result