"""Token-based phonemization (placeholder).

This module mirrors the structure of `phonemize_espeak.py` but currently
returns an empty result. It is intended to be expanded to convert input text
into model tokens grouped by sentence.
"""

from typing import List
import re
from silero_stress import load_accentor

from piper.baru_dictionary import convert


class TokensPhonemizer:
    """Placeholder token phonemizer."""

    def __init__(self) -> None:
        self.accentor = load_accentor()

    def baru_cleaners(self, text):
        replacements = [
            ("\"", "'"),
            ("–", "-"),
            ("—", "-"),
            ("«", "'"),
            ("»", "'"),
            ("\n", " "),
            ("\t", " "),

        ]
        for replacement in replacements:
            text = text.replace(replacement[0], replacement[1])
        return text

    def text_to_sequence(self, text):
        """Преобразует текст (с возможными тегами ba:/ru:) в фонемы и эмбеддинги.

        Теги:
        - ba: — далее слова башкирские
        - ru: — далее слова русские
        Если тегов нет — весь текст считается башкирским. Теги удаляются перед
        фонемизацией и извлечением эмбеддингов.
        """

        text = self.baru_cleaners(text)
        # Разбор тегов языка и удаление самих тегов
        tag_re = re.compile(r"(ba|ru):", flags=re.IGNORECASE)
        segments = []  # (lang, text_segment)
        cur_lang = 'ba'
        pos = 0
        for m in tag_re.finditer(text):
            seg = text[pos:m.start()]
            if seg:
                segments.append((cur_lang, seg))
            cur_lang = m.group(1).lower()
            pos = m.end()
        tail = text[pos:]
        if tail:
            segments.append((cur_lang, tail))
        if not segments:
            segments = [('ba', text)]

        # Проставляем ударения в русских сегментах (accentor добавляет '+')
        processed_segments = []
        for lang, seg in segments:
            if lang.lower() == 'ru':
                try:
                    seg = self.accentor(seg)
                except Exception:
                    # на случай, если модель ударений недоступна — оставляем как есть
                    pass
            processed_segments.append((lang, seg))
        segments = processed_segments

        phonemes = []
        for lang, seg in segments:
            if lang == 'ru':
                for p in convert(seg.lower(), 'ru'):
                    phonemes.append(p)
            else:
                for p in convert(seg.lower(), 'ba'):
                    phonemes.append(p)

        return phonemes

    def phonemize(self, text: str) -> List[List[str]]:
        """Convert text into tokens grouped by sentence using `text_to_sequence`.

        - Removes BOS/EOS markers ('^', '$') from the sequence since they are
          added later in phoneme->id mapping.
        - Splits into sentences on '.', '!' or '?' while keeping punctuation
          inside the sentence that ends with it.
        """
        tokens = self.text_to_sequence(text)

        # Filter out explicit BOS/EOS markers if present in the sequence
        tokens = [t for t in tokens if t not in ("^", "$")]

        all_sentences: List[List[str]] = []
        current: List[str] = []

        for tok in tokens:
            current.append(tok)
            if tok in (".", "!", "?"):
                all_sentences.append(current)
                current = []

        if current:
            all_sentences.append(current)

        return all_sentences


if __name__ == "__main__":
    phonemizer = TokensPhonemizer()
    print(phonemizer.phonemize("ru:Привет, как твои дела? ba:Минең хәлдәрем яҡшы!"))