"""Pinned, checksum-verified pretrained CLIP for local reference retrieval."""
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.request
import numpy as np
from PIL import Image,ImageOps

PACKAGE=Path(__file__).resolve().parent


def model_cache():
    return Path(os.environ.get('ANIMATION_MODEL_CACHE',str(Path(tempfile.gettempdir())/'animation-studio-clip')))


def checksum(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1048576):h.update(block)
    return h.hexdigest()


def prepare_models(cache: Path | None=None):
    cache=cache or model_cache();cache.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((PACKAGE/'models/clip-manifest.json').read_text())
    result=[]
    for item in manifest:
        path=cache/item['kind']/item['file'];path.parent.mkdir(exist_ok=True)
        if not path.exists():
            temp=path.with_suffix(path.suffix+'.part')
            with urllib.request.urlopen(item['url'],timeout=180) as source,temp.open('wb') as target:
                while chunk:=source.read(1048576):target.write(chunk)
            if checksum(temp)!=item['sha256']:
                temp.unlink();raise ValueError('Model artifact checksum verification failed')
            temp.replace(path)
        if checksum(path)!=item['sha256']:raise ValueError('Cached model checksum verification failed')
        result.append(dict(kind=item['kind'],file=item['file'],bytes=path.stat().st_size,verified=True))
    return dict(cache=str(cache),artifacts=result,model='CLIP ViT-B/32; pretrained by upstream, not trained here',
                license='MIT declared by the pinned Qdrant model cards')


@lru_cache(maxsize=2)
def session(kind,cache_string):
    import onnxruntime as ort
    ort.disable_telemetry_events()
    options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
    options.log_severity_level=3
    path=Path(cache_string)/kind/'model.onnx'
    if not path.exists():raise RuntimeError('Call prepare_reference_models first; CLIP models are not downloaded')
    return ort.InferenceSession(str(path),options,providers=['CPUExecutionProvider'])


def encode_text(texts,cache: Path | None=None):
    from tokenizers import Tokenizer
    cache=cache or model_cache()
    if not (cache/'text/tokenizer.json').exists():raise RuntimeError('Call prepare_reference_models before reference search')
    tokenizer=Tokenizer.from_file(str(cache/'text/tokenizer.json'))
    tokenizer.enable_truncation(max_length=77)
    tokenizer.enable_padding(length=77,pad_id=49407,pad_token='<|endoftext|>')
    encoded=tokenizer.encode_batch(texts)
    inputs={'input_ids':np.asarray([x.ids for x in encoded],dtype=np.int64),
            'attention_mask':np.asarray([x.attention_mask for x in encoded],dtype=np.int64)}
    vectors=session('text',str(cache)).run(['text_embeds'],inputs)[0]
    return vectors/np.maximum(np.linalg.norm(vectors,axis=1,keepdims=True),1e-12)


def encode_images(images,cache: Path | None=None):
    cache=cache or model_cache()
    settings=json.loads((cache/'vision/preprocessor_config.json').read_text())
    mean=np.asarray(settings['image_mean'],dtype=np.float32)[:,None,None]
    std=np.asarray(settings['image_std'],dtype=np.float32)[:,None,None]
    # This pinned model uses 224px center crops, matching its supplied processor.
    batch=[]
    for image in images:
        image=ImageOps.fit(image.convert('RGB'),(224,224),method=Image.Resampling.BICUBIC)
        pixels=np.asarray(image,dtype=np.float32).transpose(2,0,1)/255
        batch.append((pixels-mean)/std)
    vectors=session('vision',str(cache)).run(['image_embeds'],{'pixel_values':np.stack(batch)})[0]
    return vectors/np.maximum(np.linalg.norm(vectors,axis=1,keepdims=True),1e-12)


def search_references(query,limit=5):
    if not query.strip() or len(query)>2000 or not 1<=limit<=20:raise ValueError('Provide a query up to 2000 characters and limit 1–20')
    with np.load(PACKAGE/'models/reference-index.npz',allow_pickle=False) as z:vectors=z['embeddings']
    rows=json.loads((PACKAGE/'models/reference-index.json').read_text())
    q=encode_text([query])[0];scores=vectors@q
    order=np.argsort(scores)[::-1];seen=set();results=[]
    for i in order:
        row=rows[int(i)]
        identity=row.get('source_sha256',row['drive_id'])
        if identity in seen:continue
        seen.add(identity);results.append(dict(**row,cosine_similarity=float(scores[i])))
        if len(results)==limit:break
    return dict(query=query,results=results,
                scope='Text-to-sampled-frame CLIP retrieval; similarity is not an artistic quality score or proof the whole video matches')
