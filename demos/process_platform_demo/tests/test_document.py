"""
Tests for Document Processing Module
"""
import pytest


class TestDocumentProcessor:
    """Tests for DocumentProcessor class."""
    
    def test_processor_initialization(self):
        """Test processor initializes."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        # Should not raise
        assert processor is not None
    
    def test_classify_invoice(self):
        """Test invoice classification."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        doc_type = processor.classify_document("INVOICE\nInvoice Number: 123")
        
        assert doc_type == "Invoice"
    
    def test_classify_purchase_order(self):
        """Test purchase order classification."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        doc_type = processor.classify_document("Purchase Order\nPO Number: 456")
        
        assert doc_type == "Purchase Order"
    
    def test_classify_contract(self):
        """Test contract classification."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        doc_type = processor.classify_document("SERVICE AGREEMENT\nThis contract is between...")
        
        assert doc_type == "Contract"
    
    def test_extract_key_values_invoice_number(self, sample_invoice_text):
        """Test invoice number extraction."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        key_values = processor.extract_key_values(sample_invoice_text)
        
        # Should extract some invoice number
        assert "invoice_number" in key_values
        assert key_values["invoice_number"] is not None
    
    def test_extract_key_values_date(self, sample_invoice_text):
        """Test date extraction."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        key_values = processor.extract_key_values(sample_invoice_text)
        
        assert "date" in key_values
    
    def test_extract_key_values_total(self, sample_invoice_text):
        """Test total extraction."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        key_values = processor.extract_key_values(sample_invoice_text)
        
        assert "total" in key_values
    
    def test_extract_line_items(self, sample_invoice_text):
        """Test line item extraction."""
        from demos.document import DocumentProcessor
        
        processor = DocumentProcessor()
        line_items = processor.extract_line_items(sample_invoice_text)
        
        # Should find at least one line item
        assert len(line_items) >= 1
        
        if line_items:
            item = line_items[0]
            assert "description" in item
            assert "quantity" in item
            assert "amount" in item


class TestInvoiceProcessor:
    """Tests for InvoiceProcessor class."""
    
    def test_process_invoice(self, sample_invoice_text):
        """Test full invoice processing."""
        from demos.document import InvoiceProcessor
        
        processor = InvoiceProcessor()
        result = processor.process_invoice(sample_invoice_text)
        
        assert result["document_type"] == "Invoice"
        assert result["invoice_number"] is not None


class TestRunDemo:
    """Tests for run_demo function."""
    
    def test_run_demo_with_sample(self, sample_invoice_text):
        """Test run_demo with sample invoice."""
        from demos.document import run_demo
        
        results = run_demo(sample_invoice_text)
        
        assert "document_analysis" in results
        assert "financial_data" in results
        assert "line_items" in results
    
    def test_run_demo_default(self):
        """Test run_demo with default text."""
        from demos.document import run_demo
        
        results = run_demo()
        
        assert "document_analysis" in results
        assert results["document_analysis"]["type"] == "Invoice"
