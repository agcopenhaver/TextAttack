import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

from textattack.shared import utils
from .word_insertion import WordInsertion


class WordInsertionMaskedLM(WordInsertion):
    """Generate potential insertion for a word using a masked language model.

    Based off of:
    CLARE: Contextualized Perturbation for Textual Adversarial Attack" (Li et al, 2020):
    https://arxiv.org/abs/2009.07502

    Args:
        masked_language_model (Union[str|transformers.AutoModelForMaskedLM]): Either the name of pretrained masked language model from `transformers` model hub 
            or the actual model. Default is `bert-base-uncased`.
        max_length (int): the max sequence length the masked language model is designed to work with. Default is 512.
        max_candidates (int): maximum number of candidates to consider as replacements for each word. Replacements are
            ranked by model's confidence.
        min_confidence (float): minimum confidence threshold each replacement word must pass.
    """

    def __init__(
        self,
        masked_language_model="bert-base-uncased",
        max_length=512,
        max_candidates=50,
        min_confidence=5e-4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.max_candidates = max_candidates
        self.min_confidence = min_confidence

        self._lm_tokenizer = AutoTokenizer.from_pretrained(
            masked_language_model, use_fast=True
        )
        if isinstance(masked_language_model):
            self._language_model = AutoModelForMaskedLM.from_pretrained(
                masked_language_model
            )
        else:
            self._language_model = masked_language_model
        self._language_model.to(utils.device)
        self._language_model.eval()
        self.masked_lm_name = self._language_model.__class__.__name__

    def _encode_text(self, text):
        """Encodes ``text`` using an ``AutoTokenizer``, ``self._lm_tokenizer``.

        Returns a ``dict`` where keys are strings (like 'input_ids') and
        values are ``torch.Tensor``s. Moves tensors to the same device
        as the language model.
        """
        encoding = self._lm_tokenizer.encode_plus(
            text,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        return {k: v.to(utils.device) for k, v in encoding.items()}

    def _get_new_words(self, current_text, index):
        """Get replacement words for the word we want to replace using BAE
        method.

        Args:
            current_text (AttackedText): Text we want to get replacements for.
            index (int): index of word we want to replace
        """
        masked_attacked_text = current_text.insert_text_before_word_index(
            index, self._lm_tokenizer.mask_token
        )
        inputs = self._encode_text(masked_attacked_text.text)
        ids = inputs["input_ids"].tolist()[0]

        try:
            # Need try-except b/c mask-token located past max_length might be truncated by tokenizer
            masked_index = ids.index(self._lm_tokenizer.mask_token_id)
        except ValueError:
            return []

        with torch.no_grad():
            preds = self._language_model(**inputs)[0]

        mask_token_logits = preds[0, masked_index]
        mask_token_probs = torch.softmax(mask_token_logits, dim=0)
        ranked_indices = torch.argsort(mask_token_probs)

        replacement_words = []
        for _id in ranked_indices:
            _id = _id.item()
            token = self._lm_tokenizer.convert_ids_to_tokens(_id)
            if utils.is_one_word(token) and not utils.check_if_subword(self.masked_lm_name, token):
                if mask_token_probs[_id] > self.min_confidence:
                    replacement_words.append(token)

            if len(replacement_words) >= self.max_candidates:
                break

        return replacement_words

    def extra_repr_keys(self):
        return ["masked_lm_name ", "max_length", "max_candidates", "min_confidence"]