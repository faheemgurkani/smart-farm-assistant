#!/usr/bin/env python3
"""
Script to download TTS models for testing purposes
"""

import os
import sys
import time
import logging
import shutil

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_corrupted_models():
    """Clean up corrupted or incomplete TTS model files"""
    
    logger.info("🧹 Cleaning up corrupted TTS model files...")
    
    # TTS cache directory
    tts_cache_dir = os.path.expanduser("~/Library/Application Support/tts")
    
    if os.path.exists(tts_cache_dir):
        logger.info(f"Found TTS cache directory: {tts_cache_dir}")
        
        # List of model directories to clean
        models_to_clean = [
            "tts_models--en--ljspeech--fast_pitch",
            "tts_models--en--ljspeech--tacotron2-DDC", 
            "tts_models--en--vctk--vits"
        ]
        
        cleaned_count = 0
        for model_dir in models_to_clean:
            model_path = os.path.join(tts_cache_dir, model_dir)
            if os.path.exists(model_path):
                try:
                    shutil.rmtree(model_path)
                    logger.info(f"✅ Cleaned: {model_dir}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean {model_dir}: {e}")
        
        logger.info(f"Cleaned {cleaned_count} model directories")
    else:
        logger.info("No TTS cache directory found, nothing to clean")

def download_tts_models():
    """Download TTS models for testing"""
    
    try:
        from TTS.api import TTS
        from TTS.utils.manage import ModelManager
        logger.info("✅ Coqui TTS is available")
    except ImportError as e:
        logger.error(f"❌ Coqui TTS not available: {e}")
        logger.info("Please install: pip install coqui-tts")
        return False
    
    # List of models to download (using smaller models)
    models_to_download = [
        "tts_models/en/ljspeech/fast_pitch",  # Fast, smaller model
    ]
    
    logger.info("Starting TTS model downloads...")
    logger.info(f"Models to download: {models_to_download}")
    
    successful_downloads = []
    failed_downloads = []
    
    for model_name in models_to_download:
        logger.info(f"\n🔄 Downloading model: {model_name}")
        start_time = time.time()
        
        try:
            # Initialize TTS with the model (this triggers download)
            tts = TTS(model_name=model_name, progress_bar=True)
            
            download_time = time.time() - start_time
            logger.info(f"✅ Successfully downloaded {model_name} in {download_time:.2f} seconds")
            successful_downloads.append(model_name)
            
            # Test the model with a simple text
            test_text = "Hello, this is a test of the TTS model."
            logger.info(f"🧪 Testing model with text: '{test_text}'")
            
            # Create a temporary test file
            test_file = f"test_output_{model_name.replace('/', '_')}.wav"
            tts.tts_to_file(text=test_text, file_path=test_file)
            
            if os.path.exists(test_file):
                file_size = os.path.getsize(test_file)
                logger.info(f"✅ Test audio generated: {test_file} ({file_size} bytes)")
                # Clean up test file
                os.remove(test_file)
            else:
                logger.warning(f"⚠️ Test file not created for {model_name}")
                
        except Exception as e:
            download_time = time.time() - start_time
            logger.error(f"❌ Failed to download {model_name} after {download_time:.2f} seconds: {e}")
            failed_downloads.append(model_name)
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("="*50)
    logger.info(f"✅ Successful downloads: {len(successful_downloads)}")
    for model in successful_downloads:
        logger.info(f"  - {model}")
    
    if failed_downloads:
        logger.info(f"❌ Failed downloads: {len(failed_downloads)}")
        for model in failed_downloads:
            logger.info(f"  - {model}")
    
    logger.info("\n📁 Model files are stored in:")
    logger.info("~/Library/Application Support/tts/")
    
    return len(failed_downloads) == 0

def test_tts_functionality():
    """Test the TTS functionality with downloaded models"""
    
    logger.info("\n🧪 Testing TTS functionality...")
    
    try:
        from src.services.tts_service.tts import EnhancedTTS
        
        # Initialize TTS service
        tts_service = EnhancedTTS()
        
        # Test text
        test_text = "Hello, this is a test of the smart farm assistant TTS system."
        
        logger.info(f"Testing with text: '{test_text}'")
        
        # Generate speech
        audio_bytes = tts_service.speak(test_text, "wav")
        
        if audio_bytes:
            logger.info(f"✅ TTS test successful! Generated {len(audio_bytes)} bytes of audio")
            
            # Save test file
            test_file = "tts_test_output.wav"
            with open(test_file, 'wb') as f:
                f.write(audio_bytes)
            
            logger.info(f"💾 Test audio saved to: {test_file}")
            return True
        else:
            logger.error("❌ TTS test failed - no audio generated")
            return False
            
    except Exception as e:
        logger.error(f"❌ TTS functionality test failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("TTS Model Download and Test Script")
    logger.info("="*50)
    
    # Step 0: Clean up corrupted files
    cleanup_corrupted_models()
    
    # Step 1: Download models
    download_success = download_tts_models()
    
    if download_success:
        logger.info("\n✅ All models downloaded successfully!")
    else:
        logger.warning("\n⚠️ Some models failed to download, but continuing with test...")
    
    # Step 2: Test TTS functionality
    test_success = test_tts_functionality()
    
    # Final summary
    logger.info("\n" + "="*50)
    logger.info("FINAL SUMMARY")
    logger.info("="*50)
    logger.info(f"Model Downloads: {'✅ SUCCESS' if download_success else '❌ FAILED'}")
    logger.info(f"TTS Functionality: {'✅ SUCCESS' if test_success else '❌ FAILED'}")
    
    if download_success and test_success:
        logger.info("\n🎉 All tests passed! TTS is ready to use.")
    else:
        logger.info("\n⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 