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

        text_no_tags = "".join(seg for _, seg in segments)

        pattern_simple = r"(,.?!;:\'() )"
        text_simple = text_no_tags

        # Построим очередь языков на основе сегментов
        word_lang_queue = []
        for lang, seg in segments:
            s = seg
            for tok in re.split(pattern_simple, s.lower()):
                if not tok:
                    continue
                if re.match(pattern_simple, tok) or tok == '-' or tok == ' ':
                    continue
                word_lang_queue.append('ru' if lang.lower() == 'ru' else 'ba')

        phonemes = ["^"]
        word_index = 1
        word_lang_i = 0
        for word in re.split(pattern_simple, text_simple.lower()):
            if word == "":
                continue
            if re.match(pattern_simple, word) or word == '-':
                phonemes.append(word)
            else:
                lang = word_lang_queue[word_lang_i] if word_lang_i < len(word_lang_queue) else 'ba'
                word_lang_i += 1
                if lang == 'ru':
                    for p in convert(word, 'ru').split():
                        phonemes.append(p)
                else:
                    for p in convert(word, 'ba').split():
                        phonemes.append(p)
            if word != " ":
                word_index = word_index + 1
        phonemes.append("$")

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
