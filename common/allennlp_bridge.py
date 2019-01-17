import torch
import numpy as np

from typing import Dict, List, Iterable

from overrides import overrides

from allennlp.common.file_utils import cached_path
from allennlp.common.params import Params
from allennlp.data.vocabulary import Vocabulary


@Vocabulary.register("vocabulary_with_pretrained_vae")
class VocabularyWithPretrainedVAE(Vocabulary):
    """
    Augment the allennlp Vocabulary with filtered vocabulary
    Idea: override from_params to "set" the vocab from a file before
    constructing in a normal fashion.
    """
    @classmethod
    def from_params(cls, params: Params, instances: Iterable['adi.Instance'] = None):
        sample_vocab_file = params.pop('supervised_vocab_file')
        vae_vocab_file = params.pop('vae_vocab_file', None)
        pad_sup = params.pop('pad_sup', False)
        pad_vae = params.pop('pad_vae', False)
        pad = params.pop('pad', None)
        add_stop_end_tokens = params.pop('add_stop_end_tokens')
        vocab = cls(non_padded_namespaces=["full", "vae", "labels", "is_labeled"])

        #if `filtered_vocab_file` is a URL, redirect to the cache
        sample_vocab_file = cached_path(sample_vocab_file)
        vocab.set_from_file(filename=sample_vocab_file, namespace="full", is_padded=pad_sup or pad, oov_token="@@UNKNOWN@@")
        if add_stop_end_tokens:
            vocab.add_token_to_namespace(token="@@start@@", namespace="full")
            vocab.add_token_to_namespace(token="@@end@@", namespace="full")
        # if `full_vocab_file` is a URL, redirect to the cache
        if vae_vocab_file is not None:
            vae_vocab_file = cached_path(vae_vocab_file)
            vocab.set_from_file(filename=vae_vocab_file, namespace="vae", is_padded=pad_vae, oov_token="@@UNKNOWN@@")
            if add_stop_end_tokens:
                vocab.add_token_to_namespace(token="@@start@@", namespace="vae")
                vocab.add_token_to_namespace(token="@@end@@", namespace="vae")
        vocab.add_token_to_namespace(token="0", namespace="labels")
        vocab.add_token_to_namespace(token="1", namespace="labels")
        vocab.add_token_to_namespace(token="2", namespace="labels")
        vocab.add_token_to_namespace(token="3", namespace="labels")
        vocab.add_token_to_namespace(token="0", namespace="is_labeled")
        vocab.add_token_to_namespace(token="1", namespace="is_labeled")
        return vocab
