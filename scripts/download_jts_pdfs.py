#!/usr/bin/env python3
"""
Download JTS Clinical Practice Guidelines PDFs
Provides easy access to the Joint Trauma System CPGs
"""

import os
import sys
import requests
import zipfile
from pathlib import Path

def download_jts_pdfs():
    """Download JTS PDFs from official sources"""
    
    print("📥 JTS Clinical Practice Guidelines Downloader")
    print("=" * 50)
    
    # Create pdfs directory
    pdfs_dir = Path("pdfs")
    pdfs_dir.mkdir(exist_ok=True)
    
    print("🔍 Checking for existing PDFs...")
    existing_pdfs = list(pdfs_dir.glob("*.pdf"))
    
    if existing_pdfs:
        print(f"✅ Found {len(existing_pdfs)} existing PDFs:")
        for pdf in existing_pdfs[:5]:  # Show first 5
            print(f"   - {pdf.name}")
        if len(existing_pdfs) > 5:
            print(f"   ... and {len(existing_pdfs) - 5} more")
        
        response = input("\n❓ Do you want to download additional PDFs? (y/n): ").lower()
        if response != 'y':
            print("✅ Using existing PDFs")
            return True
    
    print("\n📋 JTS PDF Download Options:")
    print("1. Manual Download (Recommended)")
    print("2. Try Auto-Download (Limited)")
    print("3. Use Sample PDFs for Testing")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        manual_download_instructions()
    elif choice == "2":
        auto_download()
    elif choice == "3":
        create_sample_pdfs()
    else:
        print("❌ Invalid choice")
        return False
    
    return True

def manual_download_instructions():
    """Provide manual download instructions"""
    
    print("\n📥 MANUAL DOWNLOAD INSTRUCTIONS")
    print("=" * 40)
    print("1. Visit the Joint Trauma System website:")
    print("   https://jts.amedd.army.mil/")
    print()
    print("2. Navigate to 'Clinical Practice Guidelines'")
    print("3. Download the PDFs you need")
    print("4. Place them in the 'pdfs/' folder")
    print()
    print("📁 Expected PDFs (80+ files):")
    print("   - Acute_Coronary_Syndrome_14_May_2021_ID86.pdf")
    print("   - Airway_Management_of_Traumatic_Injuries_17_Jul_2017_ID39.pdf")
    print("   - Burn_Care_CPG_10_June_2025_ID12.pdf")
    print("   - Damage_Control_Resuscitation_12_Jul_2019_ID18.pdf")
    print("   - ... and many more")
    print()
    print("💡 Tip: You can download all PDFs at once if available")
    print("💡 Tip: Focus on the most relevant CPGs for your use case")
    
    input("\nPress Enter when you've downloaded the PDFs...")
    
    # Check if PDFs were added
    pdfs_dir = Path("pdfs")
    pdfs = list(pdfs_dir.glob("*.pdf"))
    
    if pdfs:
        print(f"✅ Found {len(pdfs)} PDFs in pdfs/ folder")
        return True
    else:
        print("❌ No PDFs found. Please download them manually.")
        return False

def auto_download():
    """Attempt to auto-download some sample PDFs"""
    
    print("\n🤖 AUTO-DOWNLOAD (Limited)")
    print("=" * 30)
    print("⚠️  Note: This may not work due to access restrictions")
    print("   Manual download is recommended")
    
    # Sample URLs (these may not work due to access restrictions)
    sample_urls = [
        "https://jts.amedd.army.mil/assets/docs/cpgs/Acute_Coronary_Syndrome_14_May_2021_ID86.pdf",
        "https://jts.amedd.army.mil/assets/docs/cpgs/Airway_Management_of_Traumatic_Injuries_17_Jul_2017_ID39.pdf"
    ]
    
    pdfs_dir = Path("pdfs")
    success_count = 0
    
    for url in sample_urls:
        try:
            filename = url.split('/')[-1]
            filepath = pdfs_dir / filename
            
            print(f"📥 Downloading {filename}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded {filename}")
                success_count += 1
            else:
                print(f"❌ Failed to download {filename} (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
    
    if success_count > 0:
        print(f"\n✅ Successfully downloaded {success_count} PDFs")
        return True
    else:
        print("\n❌ Auto-download failed. Please use manual download.")
        return False

def create_sample_pdfs():
    """Create sample PDFs for testing"""
    
    print("\n🧪 CREATING SAMPLE PDFS FOR TESTING")
    print("=" * 40)
    
    pdfs_dir = Path("pdfs")
    
    # Create sample content
    sample_content = {
        "sample_ketamine_protocol.txt": """
KETAMINE PROTOCOL - JTS CLINICAL PRACTICE GUIDELINE

Indications:
- RSI (Rapid Sequence Intubation)
- Pain management
- Procedural sedation

Dosage:
- RSI: 1-2 mg/kg IV
- Pain: 0.1-0.5 mg/kg IV
- Procedural: 0.5-1 mg/kg IV

Contraindications:
- Severe hypertension
- Increased ICP
- Psychiatric history

Monitoring:
- Blood pressure
- Heart rate
- Oxygen saturation
- Mental status
        """,
        
        "sample_txa_protocol.txt": """
TXA (TRANEXAMIC ACID) PROTOCOL - JTS CLINICAL PRACTICE GUIDELINE

Indications:
- Trauma bleeding
- Postpartum hemorrhage
- Major surgery

Dosage:
- Loading: 1g IV bolus over 10 minutes
- Maintenance: 1g IV over 8 hours

Timing:
- Administer within 3 hours of injury
- Maximum benefit within 1 hour

Contraindications:
- Active thrombosis
- Known hypersensitivity
- Subarachnoid hemorrhage

Monitoring:
- Thrombosis signs
- Renal function
- Vision changes
        """,
        
        "sample_burn_protocol.txt": """
BURN MANAGEMENT PROTOCOL - JTS CLINICAL PRACTICE GUIDELINE

Assessment:
- Burn depth and extent
- Airway involvement
- Associated injuries
- TBSA calculation

Initial Management:
- Stop burning process
- Remove jewelry and clothing
- Cover with clean, dry dressing
- Assess airway and breathing

Fluid Resuscitation:
- Parkland formula: 4ml x TBSA% x weight(kg)
- Half in first 8 hours
- Half in next 16 hours

Pain Management:
- IV opioids as needed
- Consider ketamine for procedures
- Monitor for respiratory depression

Monitoring:
- Urine output
- Vital signs
- Pain control
- Wound progression
        """
    }
    
    try:
        # Create sample text files (since we can't easily create PDFs)
        for filename, content in sample_content.items():
            filepath = pdfs_dir / filename
            with open(filepath, 'w') as f:
                f.write(content.strip())
            print(f"✅ Created {filename}")
        
        print(f"\n✅ Created {len(sample_content)} sample protocol files")
        print("💡 These are text files that can be processed by the system")
        print("💡 For production use, download actual JTS PDFs")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample files: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 JTS PDF Downloader")
    print("This script helps you get the JTS Clinical Practice Guidelines")
    print("needed for the trauma assistant to work properly.\n")
    
    success = download_jts_pdfs()
    
    if success:
        print("\n🎉 Setup complete!")
        print("Next steps:")
        print("1. Run: python3 scripts/build_index.py")
        print("2. Run: python3 scripts/ask_conversational.py")
    else:
        print("\n❌ Setup incomplete. Please download PDFs manually.")

if __name__ == "__main__":
    main() 