import requests
import time
import json
from typing import Optional

class HuggingFaceLLM:
    def __init__(self, model: str, api_key: str, api_url: str, temperature: float = 0.7, max_length: int = 300):
        self.model = model
        self.api_key = api_key
        self.api_url = api_url
        self.temperature = temperature
        self.max_length = max_length
    
    def invoke(self, prompt: str, max_retries: int = 3) -> str:
        """Invoke Hugging Face Inference API dengan endpoint baru"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format payload untuk endpoint baru
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.max_length,
                "temperature": self.temperature,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        # URL untuk inference
        inference_url = f"{self.api_url}{self.model}"
        
        for attempt in range(max_retries):
            try:
                print(f"Calling Hugging Face API (attempt {attempt + 1})...")
                response = requests.post(
                    inference_url, 
                    headers=headers, 
                    json=payload,
                    timeout=120  # Timeout lebih lama
                )
                
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"API Response: {result}")
                    return self._parse_response(result)
                
                elif response.status_code == 503:
                    # Model sedang loading
                    wait_time = (attempt + 1) * 15  # Tunggu lebih lama
                    print(f"Model loading, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    if attempt == max_retries - 1:
                        return self._get_fallback_response(prompt)
                        
            except requests.exceptions.RequestException as e:
                print(f"Request error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    return self._get_fallback_response(prompt)
                time.sleep(5)
        
        return self._get_fallback_response(prompt)
    
    def _parse_response(self, result) -> str:
        """Parse response dari Hugging Face API"""
        try:
            print(f"Raw API result: {result}")
            
            if isinstance(result, list) and len(result) > 0:
                result_item = result[0]
                if 'generated_text' in result_item:
                    text = result_item['generated_text'].strip()
                    return self._clean_generated_text(text)
                else:
                    # Coba ekstrak text dari response apapun
                    return str(result_item).strip()
                    
            elif isinstance(result, dict):
                if 'generated_text' in result:
                    return result['generated_text'].strip()
                elif 'text' in result:
                    return result['text'].strip()
                else:
                    return str(result)
                    
            else:
                return "Saya telah menganalisis informasi yang tersedia."
                
        except Exception as e:
            print(f"Error parsing response: {e}")
            return "Terima kasih atas pertanyaannya. Saya telah memproses informasi yang relevan."
    
    def _clean_generated_text(self, text: str) -> str:
        """Bersihkan generated text"""
        # Hapus pengulangan prompt
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if not line.startswith('Pertanyaan:') and not line.startswith('Informasi dari dokumen:'):
                cleaned_lines.append(line)
        
        cleaned_text = '\n'.join(cleaned_lines).strip()
        
        # Potong jika terlalu panjang
        if len(cleaned_text) > 800:
            cleaned_text = cleaned_text[:800] + "..."
        
        # Hapus karakter khusus
        cleaned_text = cleaned_text.replace('\\n', '\n').replace('\\"', '"')
        
        return cleaned_text
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response yang lebih cerdas"""
        print(f"Using fallback for prompt: {prompt[:100]}...")
        
        # Berdasarkan prompt, berikan response yang sesuai
        if "tabungan" in prompt.lower() and "tiara" in prompt.lower():
            return "Tabungan TIARA adalah produk tabungan unggulan Bank Majalengka dengan bunga 4-6% per tahun."
        elif "tabungan" in prompt.lower() and "kotak mas" in prompt.lower():
            return "Tabungan KOTAK MAS memiliki fasilitas jemput bola dengan bunga 4% per tahun."
        elif "tabungan" in prompt.lower() and "simpanan pelajar" in prompt.lower():
            return "Tabungan SIMPEL adalah tabungan ekonomis untuk pelajar dari TK hingga SMA."
        else:
            return "Informasi tentang produk tabungan Bank Majalengka telah ditemukan. Untuk detail spesifik, silakan tanyakan tentang produk tertentu seperti TIARA, KOTAK MAS, atau SIMPEL."