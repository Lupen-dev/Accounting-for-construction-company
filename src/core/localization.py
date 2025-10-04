import json
from pathlib import Path

# Available languages
LANGUAGES = {
    'tr': 'Türkçe',
    'en': 'English',
    'id': 'Bahasa Indonesia'
}

# Current language
current_language = 'tr'

# Translations dictionary
translations = {}

def load_translations():
    """Load translation files for all languages"""
    global translations
    translations_dir = Path('translations')
    
    for lang in LANGUAGES.keys():
        lang_file = translations_dir / f"{lang}.json"
        if lang_file.exists():
            with open(lang_file, 'r', encoding='utf-8') as f:
                translations[lang] = json.load(f)

def setup_translations():
    """Initialize translation system"""
    # Create translations directory if it doesn't exist
    Path('translations').mkdir(exist_ok=True)
    
    # Create language files if they don't exist
    create_default_translations()
    
    # Load all translations
    load_translations()

def create_default_translations():
    """Create default translation files for all supported languages"""
    translations_dir = Path('translations')
    
    # Default translations structure
    default_translations = {
        'tr': {
            'app_name': 'İnşaat Muhasebe Sistemi',
            'menu': {
                'customers': 'Cari Hesaplar',
                'cheques': 'Çek/Senet',
                'employees': 'Personel',
                'properties': 'Tapu/Taşınmaz',
                'payments': 'Taksit/Ödeme',
                'trade': 'Ticaret',
                'reports': 'Raporlar',
                'settings': 'Ayarlar'
            }
        },
        'en': {
            'app_name': 'Construction Accounting System',
            'menu': {
                'customers': 'Accounts',
                'cheques': 'Cheques/Bills',
                'employees': 'Employees',
                'properties': 'Properties/Deeds',
                'payments': 'Payments',
                'trade': 'Trade',
                'reports': 'Reports',
                'settings': 'Settings'
            }
        },
        'id': {
            'app_name': 'Sistem Akuntansi Konstruksi',
            'menu': {
                'customers': 'Akun',
                'cheques': 'Cek/Tagihan',
                'employees': 'Karyawan',
                'properties': 'Properti/Sertifikat',
                'payments': 'Pembayaran',
                'trade': 'Perdagangan',
                'reports': 'Laporan',
                'settings': 'Pengaturan'
            }
        }
    }
    
    # Create translation files
    for lang, trans in default_translations.items():
        lang_file = translations_dir / f"{lang}.json"
        if not lang_file.exists():
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(trans, f, ensure_ascii=False, indent=4)

def get_text(key, language=None):
    """Get translated text for a key in the specified language"""
    if language is None:
        language = current_language
    
    try:
        # Split the key by dots to support nested translations
        keys = key.split('.')
        value = translations[language]
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return key  # Return the key itself if translation not found

def set_language(language):
    """Change the current language"""
    global current_language
    if language in LANGUAGES:
        current_language = language
        return True
    return False