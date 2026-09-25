#!/usr/bin/env python3
"""
Extract content from WatchLockAI foundational DOCX documents
"""

import os
import json
from zipfile import ZipFile
import xml.etree.ElementTree as ET

def extract_docx_text(docx_path):
    """Extract text content from a DOCX file"""
    try:
        with ZipFile(docx_path, 'r') as docx:
            # Read the main document content
            document_xml = docx.read('word/document.xml')
            
            # Parse XML
            root = ET.fromstring(document_xml)
            
            # Extract text from all text nodes
            text_content = []
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    text_content.append(elem.text.strip())
            
            return '\n'.join(text_content)
    
    except Exception as e:
        print(f"Error extracting {docx_path}: {e}")
        return None

def main():
    base_path = "/workspace/user_input_files"
    
    documents = [
        "WatchLockAI.docx",
        "WATCHLOCKAI THE FOUNDATION OF THE NEXT GENERATION AGENTIC SOC.docx", 
        "Watchlock_v_.9_build_guide.docx",
        "watchlock_v_01_plan.docx"
    ]
    
    extracted_content = {}
    
    for doc in documents:
        doc_path = os.path.join(base_path, doc)
        if os.path.exists(doc_path):
            print(f"Extracting content from: {doc}")
            content = extract_docx_text(doc_path)
            if content:
                extracted_content[doc] = content
                print(f"[PASS] Extracted {len(content)} characters from {doc}")
                
                # Save individual file
                output_file = f"/workspace/foundational_docs/{doc.replace('.docx', '_content.txt')}"
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[PASS] Saved to: {output_file}")
            else:
                print(f"[FAIL] Failed to extract content from {doc}")
        else:
            print(f"[FAIL] File not found: {doc_path}")
    
    # Save combined analysis
    combined_file = "/workspace/foundational_docs/combined_analysis.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_content, f, indent=2, ensure_ascii=False)
    
    print(f"\n[PASS] Combined analysis saved to: {combined_file}")
    print(f"[BARS] Total documents processed: {len(extracted_content)}")
    
    return extracted_content

if __name__ == "__main__":
    main()
