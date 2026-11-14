"""Train a small supervised narration-intent classifier; export safe numeric data."""
from pathlib import Path
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from scipy.sparse import hstack
from sklearn.metrics import classification_report,confusion_matrix


def main():
    root=Path(__file__).resolve().parents[1]
    corpus=json.loads((root/'training/reaction_corpus.json').read_text())
    texts=[];labels=[]
    for label,examples in corpus['train'].items():
        texts.extend(examples);labels.extend([label]*len(examples))
    test=[x['text'] for x in corpus['test']]
    assert not set(t.lower() for t in texts)&set(t.lower() for t in test)
    word=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True)
    char=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),sublinear_tf=True)
    x=hstack([word.fit_transform(texts),char.fit_transform(texts)])
    model=LogisticRegression(C=7,class_weight='balanced',max_iter=2000,random_state=7).fit(x,labels)
    target=[x['label'] for x in corpus['test']]
    pred=model.predict(hstack([word.transform(test),char.transform(test)]))
    out=root/'src/animation_mcp/models';out.mkdir(exist_ok=True)
    data=dict(classes=model.classes_.tolist(),word_vocabulary=word.vocabulary_,word_idf=word.idf_.tolist(),
              char_vocabulary=char.vocabulary_,char_idf=char.idf_.tolist(),
              provenance=corpus['provenance'],task='narration-intent classification; not generative drawing or RL')
    # Convert NumPy integer vocabulary entries for portable JSON.
    data['word_vocabulary']={k:int(v) for k,v in word.vocabulary_.items()}
    data['char_vocabulary']={k:int(v) for k,v in char.vocabulary_.items()}
    (out/'reaction_classifier.json').write_text(json.dumps(data,sort_keys=True)+'\n')
    np.savez_compressed(out/'reaction_classifier.npz',coef=model.coef_,intercept=model.intercept_)
    report=dict(train_examples=len(texts),test_examples=len(test),accuracy=float(np.mean(pred==target)),
                split='fixed hand-authored sentence holdout; shares vocabulary and author with training',
                evaluation=classification_report(target,pred,output_dict=True,zero_division=0),
                predictions=[dict(text=t,expected=y,predicted=str(p)) for t,y,p in zip(test,target,pred)],
                limitations='Small synthetic English corpus. No claim of general language, audiovisual understanding, artistic quality or training from reference videos.')
    report_path=root/'output/research/reaction-training.json'
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
