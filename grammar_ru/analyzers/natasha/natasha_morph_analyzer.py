from .natasha_analyzer import NatashaAnalyzer
import pandas as pd
from slovnet import Morph
from typing import *


class NatashaMorphAnalyzer(NatashaAnalyzer):
    def __init__(self):
        # TODO: Add required columns
        self.morph = Morph.load('models/slovnet_morph_news_v1.tar', batch_size=4)
        super(NatashaMorphAnalyzer, self).__init__()

    def analyze_chunks(self, df: pd.DataFrame, chunks: List[List[str]]) -> pd.DataFrame:
        morph_chunks = []
        for i, morph_res in enumerate(self.morph.map(chunks)):
            morph_chunks.append({})
            for j, morph_token in enumerate(morph_res.tokens):
                morph_chunks[-1]["POS"] = morph_token.pos
                for feat in morph_token.feats.keys():
                    morph_chunks[-1][feat] = morph_token.feats[feat]

        # TODO: List of dictionaries to rows
        raise NotImplementedError()
