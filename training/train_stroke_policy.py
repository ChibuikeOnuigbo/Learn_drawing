"""Bounded supervised research baseline on original procedural Bezier strokes.

Learns points along a supplied curve, not what to draw. Whole control polygons
are disjoint between train/validation/test. Analytic interpolation is the exact
zero-error production baseline; this does NOT demonstrate an advantage over it.
"""
import argparse
import copy
import json
from pathlib import Path
import time
import numpy as np
from sklearn.neural_network import MLPRegressor
from threadpoolctl import threadpool_limits


def dataset(seed, count):
    rng=np.random.default_rng(seed)
    controls=rng.uniform(.05,.95,(count,4,2))
    t=np.linspace(0,1,17)
    x=np.concatenate([np.repeat(controls.reshape(count,1,8),len(t),axis=1),
                      np.broadcast_to(t[None,:,None],(count,len(t),1))],axis=2)
    bases=np.stack([(1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3],axis=1)
    y=np.einsum('tf,cfd->ctd',bases,controls)
    return controls,x.reshape(-1,9)*2-1,y.reshape(-1,2)


def run(folder: Path, epochs=160):
    folder.mkdir(parents=True,exist_ok=True)
    train_c,x,y=dataset(100,600)
    val_c,vx,vy=dataset(200,120)
    test_c,tx,ty=dataset(300,120)
    model=MLPRegressor(hidden_layer_sizes=(64,64),activation='tanh',solver='adam',
                       learning_rate_init=.002,batch_size=256,random_state=7)
    start=time.monotonic()
    log=[]
    best_error=float('inf')
    best=None
    with threadpool_limits(limits=1):
        for epoch in range(1,epochs+1):
            model.partial_fit(x,y)
            if epoch == 1 or epoch % 10 == 0 or epoch == epochs:
                error=float(np.abs(model.predict(vx)-vy).mean())
                log.append({'epoch':epoch,'validation_mae':error})
                if error < best_error:
                    best_error=error
                    best=copy.deepcopy(model)
                print(epoch,error,flush=True)
        pred=best.predict(tx)
    params={f'coef_{i}':w for i,w in enumerate(best.coefs_)}
    params.update({f'intercept_{i}':b for i,b in enumerate(best.intercepts_)})
    np.savez_compressed(folder/'stroke_policy.npz',**params)
    report={
        'task':'Given four control points and progress t, predict a cubic Bezier point',
        'training':'supervised Adam; not reinforcement learning',
        'train_curves':len(train_c),'validation_curves':len(val_c),'test_curves':len(test_c),
        'split':'independent whole curves from seeds 100/200/300; fixed test evaluated once',
        'epochs':epochs,'validation_log':log,'selected_validation_mae':best_error,
        'test_mae':float(np.abs(pred-ty).mean()),
        'test_error_pixels_at_256':float(np.abs(pred-ty).mean()*256),
        'stationary_start_point_test_mae':float(np.abs(np.repeat(test_c[:,0,:],17,axis=0)-ty).mean()),
        'analytic_bezier_baseline_mae':0.0,
        'seconds':time.monotonic()-start,
        'limits':'Synthetic curves only. Cannot choose subjects, draw anatomy, compose scenes or animate characters. Exact geometry remains better for production.'}
    (folder/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    # Test samples show teacher (gray) against learned points (cyan).
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="512" viewBox="0 0 1024 512">',
           '<rect width="1024" height="512" fill="#101b2d"/>']
    pred=pred.reshape(-1,17,2);truth=ty.reshape(-1,17,2)
    for i in range(8):
        dx,dy=(i%4)*256,(i//4)*256
        for arr,color,width in [(truth[i],'#f5b45b',5),(pred[i],'#66e3e0',2)]:
            points=' '.join(f'{dx+a*256:.3f},{dy+b*256:.3f}' for a,b in arr)
            parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    parts.append('</svg>')
    (folder/'heldout-strokes.svg').write_text('\n'.join(parts))
    print(json.dumps(report,indent=2))
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('output/stroke-training'))
    parser.add_argument('--epochs',type=int,default=160)
    args=parser.parse_args()
    if not 1<=args.epochs<=1000:parser.error('Use 1–1000 epochs per bounded experiment')
    run(args.output,args.epochs)
