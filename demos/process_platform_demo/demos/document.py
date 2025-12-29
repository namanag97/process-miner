"""
Intelligent Document Processing Demo
Using spaCy for NLP and Entity Extraction
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ExtractedEntity:
    """Represents an extracted entity."""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class DocumentAnalysis:
    """Results of document analysis."""
    document_type: str
    entities: List[ExtractedEntity]
    key_values: Dict[str, str]
    summary: str


class DocumentProcessor:
    """
    Intelligent Document Processing using NLP.
    
    Capabilities:
    1. Document Classification
    2. Named Entity Recognition (NER)
    3. Key-Value Extraction
    4. Regex-based field extraction
    """
    
    def __init__(self):
        self.nlp = None
        self._load_nlp()
    
    def _load_nlp(self):
        """Load spaCy model."""
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Model not installed, use blank
                print("Note: spaCy model not found. Using basic extraction.")
                self.nlp = None
        except ImportError:
            print("Note: spaCy not installed. Using regex-based extraction only.")
            self.nlp = None
    
    def classify_document(self, text: str) -> str:
        """Classify document type based on keywords."""
        text_lower = text.lower()
        
        if 'invoice' in text_lower:
            return 'Invoice'
        elif 'purchase order' in text_lower or 'po number' in text_lower:
            return 'Purchase Order'
        elif 'contract' in text_lower or 'agreement' in text_lower:
            return 'Contract'
        elif 'receipt' in text_lower:
            return 'Receipt'
        elif 'quote' in text_lower or 'quotation' in text_lower:
            return 'Quote'
        else:
            return 'General Document'
    
    def extract_entities_spacy(self, text: str) -> List[ExtractedEntity]:
        """Extract named entities using spaCy."""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append(ExtractedEntity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            ))
        
        return entities
    
    def extract_key_values(self, text: str) -> Dict[str, str]:
        """
        Extract key-value pairs from document using regex patterns.
        """
        patterns = {
            'invoice_number': [
                r'Invoice\s*(?:#|No\.?|Number)?\s*:?\s*([A-Z0-9-]+)',
                r'INV[-#](\d+)'
            ],
            'date': [
                r'Date\s*:?\s*(\w+\s+\d{1,2},?\s+\d{4})',
                r'Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ],
            'due_date': [
                r'Due\s*Date\s*:?\s*(\w+\s+\d{1,2},?\s+\d{4})',
                r'Due\s*Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ],
            'total': [
                r'Total\s*:?\s*\$?([\d,]+\.?\d*)',
                r'TOTAL\s*:?\s*\$?([\d,]+\.?\d*)',
                r'Amount\s+Due\s*:?\s*\$?([\d,]+\.?\d*)'
            ],
            'subtotal': [
                r'Subtotal\s*:?\s*\$?([\d,]+\.?\d*)',
                r'Sub-?Total\s*:?\s*\$?([\d,]+\.?\d*)'
            ],
            'tax': [
                r'Tax\s*\(?[\d.]*%?\)?\s*:?\s*\$?([\d,]+\.?\d*)',
                r'VAT\s*:?\s*\$?([\d,]+\.?\d*)'
            ],
            'payment_terms': [
                r'Payment\s*Terms?\s*:?\s*(Net\s*\d+)',
                r'Terms?\s*:?\s*(Due\s+on\s+Receipt|Net\s*\d+)'
            ],
            'po_number': [
                r'PO\s*(?:#|No\.?|Number)?\s*:?\s*([A-Z0-9-]+)',
                r'Purchase\s*Order\s*:?\s*([A-Z0-9-]+)'
            ],
            'account_number': [
                r'Account\s*(?:#|No\.?)?\s*:?\s*(\d+)',
                r'Bank\s*Account\s*:?\s*([A-Z0-9]+)'
            ]
        }
        
        extracted = {}
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted[field] = match.group(1).strip()
                    break
        
        return extracted
    
    def extract_line_items(self, text: str) -> List[Dict]:
        """Extract line items from tabular data in document."""
        # Simple pattern for line items: description, quantity, price, amount
        line_pattern = r'([A-Za-z\s&]+)\s+(\d+)\s+\$?([\d,]+\.?\d*)\s+\$?([\d,]+\.?\d*)'
        
        items = []
        for match in re.finditer(line_pattern, text):
            items.append({
                'description': match.group(1).strip(),
                'quantity': int(match.group(2)),
                'unit_price': float(match.group(3).replace(',', '')),
                'amount': float(match.group(4).replace(',', ''))
            })
        
        return items
    
    def analyze_document(self, text: str) -> DocumentAnalysis:
        """
        Perform full document analysis.
        """
        doc_type = self.classify_document(text)
        entities = self.extract_entities_spacy(text)
        key_values = self.extract_key_values(text)
        
        # Generate summary
        summary_parts = [f"Document Type: {doc_type}"]
        
        if key_values.get('invoice_number'):
            summary_parts.append(f"Invoice: {key_values['invoice_number']}")
        if key_values.get('total'):
            summary_parts.append(f"Total: ${key_values['total']}")
        if key_values.get('date'):
            summary_parts.append(f"Date: {key_values['date']}")
        
        # Count entity types
        entity_counts = {}
        for ent in entities:
            entity_counts[ent.label] = entity_counts.get(ent.label, 0) + 1
        
        if entity_counts:
            entity_summary = ", ".join([f"{count} {label}" for label, count in entity_counts.items()])
            summary_parts.append(f"Entities found: {entity_summary}")
        
        return DocumentAnalysis(
            document_type=doc_type,
            entities=entities,
            key_values=key_values,
            summary=" | ".join(summary_parts)
        )


class InvoiceProcessor(DocumentProcessor):
    """Specialized processor for invoices."""
    
    def process_invoice(self, text: str) -> Dict:
        """Extract all invoice-specific information."""
        analysis = self.analyze_document(text)
        line_items = self.extract_line_items(text)
        
        # Find vendor and customer from entities
        orgs = [e.text for e in analysis.entities if e.label == 'ORG']
        
        return {
            'document_type': 'Invoice',
            'invoice_number': analysis.key_values.get('invoice_number'),
            'date': analysis.key_values.get('date'),
            'due_date': analysis.key_values.get('due_date'),
            'vendor': orgs[0] if orgs else None,
            'customer': orgs[1] if len(orgs) > 1 else None,
            'subtotal': analysis.key_values.get('subtotal'),
            'tax': analysis.key_values.get('tax'),
            'total': analysis.key_values.get('total'),
            'payment_terms': analysis.key_values.get('payment_terms'),
            'line_items': line_items,
            'all_entities': [{'text': e.text, 'type': e.label} for e in analysis.entities]
        }


def run_demo(sample_text: str = None) -> Dict:
    """Run the IDP demo."""
    
    if sample_text is None:
        sample_text = """
        INVOICE
        
        Invoice Number: INV-2024-00789
        Date: December 28, 2024
        Due Date: January 27, 2025
        
        Bill To:
        Acme Corporation
        123 Business Street
        New York, NY 10001
        
        Ship To:
        John Smith
        456 Delivery Lane
        Los Angeles, CA 90001
        
        Description                     Qty    Unit Price    Amount
        ----------------------------------------------------------------
        Professional Services           10     $150.00       $1,500.00
        Software License               1      $2,500.00     $2,500.00
        Support & Maintenance          1      $500.00       $500.00
        
        ----------------------------------------------------------------
        Subtotal:                                           $4,500.00
        Tax (8%):                                           $360.00
        ----------------------------------------------------------------
        TOTAL:                                              $4,860.00
        
        Payment Terms: Net 30
        Please remit payment to: First National Bank Account: 123456789
        
        Thank you for your business!
        """
    
    processor = InvoiceProcessor()
    result = processor.process_invoice(sample_text)
    
    # Format for display
    return {
        'document_analysis': {
            'type': result['document_type'],
            'invoice_number': result['invoice_number'],
            'date': result['date'],
            'due_date': result['due_date'],
            'payment_terms': result['payment_terms']
        },
        'financial_data': {
            'subtotal': result['subtotal'],
            'tax': result['tax'],
            'total': result['total']
        },
        'parties': {
            'vendor': result['vendor'],
            'customer': result['customer']
        },
        'line_items': result['line_items'],
        'entities_found': result['all_entities'][:10]  # Limit for display
    }
