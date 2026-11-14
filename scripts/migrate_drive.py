"""Restore the user's Drive files with checksum verification; never commit cookies.

Run with the research extra installed. Downloads do not execute imported code.
"""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import zipfile
import gdown


def safe_extract(archive, destination):
    destination=destination.resolve()
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist())>20000 or sum(i.file_size for i in z.infolist())>5_000_000_000:
            raise ValueError('Archive exceeds extraction budget')
        for item in z.infolist():
            if not (destination/item.filename).resolve().is_relative_to(destination):
                raise ValueError('Archive path escapes destination')
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('Symlink archive entry rejected')
        bad=z.testzip()
        if bad:raise ValueError(f'CRC check failed: {bad}')
        z.extractall(destination)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('/workspace/drawing-data/drive'))
    parser.add_argument('--extract',action='store_true')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    manifest=Path(__file__).resolve().parents[1]/'migration/drive_manifest.json'
    for item in json.loads(manifest.read_text()):
        name=item['name']
        if Path(name).name != name:raise ValueError('Invalid manifest basename')
        path=args.output/name
        if not path.exists():
            temp=path.with_suffix(path.suffix+'.part')
            gdown.download(id=item['id'],output=str(temp),use_cookies=False,verify=True)
            if not temp.is_file():raise RuntimeError(f'Download failed: {name}')
            digest=hashlib.sha256(temp.read_bytes()).hexdigest()
            if digest != item['sha256']:raise ValueError(f'Checksum mismatch: {name}')
            temp.rename(path)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item['sha256']:raise ValueError(f'Checksum mismatch: {name}')
        print('Verified:',name)
        if args.extract and path.suffix=='.zip':
            safe_extract(path,args.output/'extracted'/path.stem)


if __name__=='__main__':main()
