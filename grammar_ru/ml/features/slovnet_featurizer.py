from .architecture import *
from navec import Navec
from slovnet import Syntax, Morph
from ...common import Loc
from yo_fluq_ds import *

class SlovnetFeaturizer(Featurizer):
    def __init__(self):
        self.navec = Navec.load(Loc.dependencies_path/'navec_news_v1_1B_250K_300d_100q.tar')
        self.syntax = Syntax.load(Loc.dependencies_path/'slovnet_syntax_news_v1.tar')
        self.syntax.navec(self.navec)
        self.morph = Morph.load(Loc.dependencies_path/'slovnet_morph_news_v1.tar')
        self.morph.navec(self.navec)


    def get_name(self):
        return 'slovnet'

    @staticmethod
    def separate_df_to_text(df):
        chunks = dict(
            sentences=[],
            ids=[]
        )
        last_sentence = -1
        for row in Query.df(df):
            if row['sentence_id'] != last_sentence:
                chunks['sentences'].append([])
                last_sentence = row['sentence_id']
            chunks['sentences'][-1].append(row['word'])
            chunks['ids'].append(dict(word_id=row['word_id'], sentence_id=row['sentence_id']))
        return chunks


    def _build_morph(self, chunks):
        morph_chunks = []
        counter = 0
        for i, morph_res in enumerate(self.morph.map(chunks['sentences'])):
            for j, morph_token in enumerate(morph_res.tokens):
                morph_chunks.append({})
                morph_chunks[-1]["POS"] = morph_token.pos
                for feat in morph_token.feats.keys():
                    morph_chunks[-1][feat] = morph_token.feats[feat]
                morph_chunks[-1]['word_id'] = chunks['ids'][counter]['word_id']
                counter += 1
        mdf = pd.DataFrame(morph_chunks)
        mdf = mdf.set_index('word_id')
        return mdf

    def _build_syntax(self, chunks):
        counter = 0
        syntax_chunks = []
        for i, syntax_res in enumerate(self.syntax.map(chunks['sentences'])):
            for j, syntax_token in enumerate(syntax_res.tokens):
                syntax_chunks.append({})
                syntax_chunks[-1]["syntax_head_id"] = int(syntax_token.head_id)
                syntax_chunks[-1]["syntax_id"] = int(syntax_token.id)
                syntax_chunks[-1]['relation'] = syntax_token.rel

                for key, value in chunks['ids'][counter].items():
                    syntax_chunks[-1][key] = value
                counter += 1

        pdf = pd.DataFrame(syntax_chunks)
        pdf = pdf.merge(
            pdf.set_index(['sentence_id', 'syntax_id']).word_id.to_frame('syntax_parent_id'),
            left_on=['sentence_id', 'syntax_head_id'],
            right_index=True,
            how='left'
        )
        pdf.syntax_parent_id = pdf.syntax_parent_id.fillna(-1).astype(int)
        pdf = pdf.drop(['syntax_head_id', 'syntax_id', 'sentence_id'], axis=1).set_index('word_id')
        return pdf

    def featurize(self, df):
        chunks = SlovnetFeaturizer.separate_df_to_text(df)
        mdf = self._build_morph(chunks)
        pdf = self._build_syntax(chunks)
        return mdf.merge(pdf,left_index=True, right_index=True)


