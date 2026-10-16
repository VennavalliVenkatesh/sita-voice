import os
from collections.abc import Iterable

import logging
logging.basicConfig(level=logging.WARNING)

from .base_engine import BaseEngineTransformer, LANG_LIST_FILE

F_DIR = os.path.dirname(os.path.realpath(__file__))

MODEL_DOWNLOAD_URL = 'https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/indicxlit-indic-en-v1.0.zip'
DICTS_DOWNLOAD_URL = 'https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/word_prob_dicts_en.zip'
XLIT_VERSION = "v1.0" # If model/dict is changed on the storage, do not forget to change this variable in-order to force-download new assets

def is_folder_writable(folder):
    try:
        os.makedirs(folder, exist_ok=True)
        tmp_file = os.path.join(folder, '.write_test')
        with open(tmp_file, 'w') as f:
            f.write('Permission Check')
        os.remove(tmp_file)
        return True
    except:
        return False

def is_directory_writable(path):
    if os.name == 'nt':
        return is_folder_writable(path)
    return os.access(path, os.W_OK | os.X_OK)

class XlitEngineTransformer_Indic2En(BaseEngineTransformer):
    """
    For Managing the top level tasks and applications of transliteration

    TODO: Ability to pass `beam_width` dynamically
    """
    def __init__(self, beam_width=4, rescore=True):
        if is_directory_writable(F_DIR):
            models_path = os.path.join(F_DIR, 'models')
        else:
            user_home = os.path.expanduser("~")
            models_path = os.path.join(user_home, '.AI4Bharat_Xlit_Models')
        models_path = os.path.join(models_path, "indic2en", XLIT_VERSION)
        os.makedirs(models_path, exist_ok=True)

        canonical_bundled = os.path.join(F_DIR, 'models', 'indic2en', 'lang_list.txt')
        target_lang_list = os.path.join(models_path, 'lang_list.txt')

        # Find best existing lang_list file or create it
        lang_list_file = None
        for candidate in [target_lang_list, canonical_bundled, os.path.join(models_path, LANG_LIST_FILE)]:
            if os.path.isfile(candidate):
                lang_list_file = candidate
                break

        if lang_list_file is None:
            # Create the file in models_path and parent directory if missing
            default_langs = "en\nas\nbn\nbrx\ngom\ngu\nhi\nkn\nks\nmai\nml\nmni\nmr\nne\nor\npa\nsa\nsd\nsi\nta\nte\nur\n"
            for target_path in [target_lang_list, canonical_bundled]:
                try:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(default_langs)
                    lang_list_file = target_path
                    break
                except Exception:
                    continue

        if lang_list_file and os.path.isfile(lang_list_file):
            _all_supported_langs = open(lang_list_file, encoding='utf-8').read().strip().split('\n')
        else:
            _all_supported_langs = ["en", "as", "bn", "brx", "gom", "gu", "hi", "kn", "ks", "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sd", "si", "ta", "te", "ur"]
        self._all_supported_langs = set(_all_supported_langs)
        if "en" in self._all_supported_langs:
            self._all_supported_langs.remove("en")

        self._tgt_langs = set(["en"])

        model_file_path = self.download_models(models_path, MODEL_DOWNLOAD_URL)
        if rescore:
            dicts_folder = self.download_dicts(models_path, DICTS_DOWNLOAD_URL)
        else:
            dicts_folder = None
        
        super().__init__(models_path, beam_width=beam_width, rescore=rescore, lang_list_file=lang_list_file)
    
    @property
    def all_supported_langs(self):
        return self._all_supported_langs

    @property
    def tgt_langs(self):
        return self._tgt_langs
    
    def translit_word(self, word, lang_code, topk=4):
        if lang_code not in self.all_supported_langs:
            raise NotImplementedError(f"Language: `{lang_code}` not yet supported")
        return self._transliterate_word(word, src_lang=lang_code, tgt_lang='en', topk=topk)
    
    def translit_sentence(self, indic_sentence, lang_code):
        if lang_code not in self.all_supported_langs:
            raise NotImplementedError(f"Language: `{lang_code}` not yet supported")
        return self._transliterate_sentence(indic_sentence, src_lang=lang_code, tgt_lang='en')
