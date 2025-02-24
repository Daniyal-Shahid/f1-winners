import nltk
import ssl

def download_nltk_dependencies():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    dependencies = [
        'punkt',
        'averaged_perceptron_tagger',
        'brown',
        'wordnet',
        'omw-1.4'
    ]
    
    for package in dependencies:
        print(f"Downloading {package}...")
        nltk.download(package)

if __name__ == "__main__":
    download_nltk_dependencies() 