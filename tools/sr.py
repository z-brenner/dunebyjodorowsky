"""Minimal Real-ESRGAN compact-model runner (CPU)."""
import torch, torch.nn as nn, torch.nn.functional as F, numpy as np

class SRVGGNetCompact(nn.Module):
    def __init__(self, num_feat=64, num_conv=32, upscale=4):
        super().__init__()
        self.upscale = upscale
        self.body = nn.ModuleList([nn.Conv2d(3, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)])
        for _ in range(num_conv):
            self.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1)); self.body.append(nn.PReLU(num_parameters=num_feat))
        self.body.append(nn.Conv2d(num_feat, 3 * upscale * upscale, 3, 1, 1))
        self.upsampler = nn.PixelShuffle(upscale)
    def forward(self, x):
        out = x
        for m in self.body: out = m(out)
        return self.upsampler(out) + F.interpolate(x, scale_factor=self.upscale, mode="nearest")

def load(path, num_conv):
    sd = torch.load(path, map_location="cpu")
    sd = sd.get("params_ema", sd.get("params", sd))
    m = SRVGGNetCompact(num_conv=num_conv); m.load_state_dict(sd, strict=True); m.eval(); return m

@torch.no_grad()
def upscale(model, rgb, tile=384, pad=16):
    """rgb: HxWx3 uint8 -> 4x uint8, processed in overlapping tiles."""
    h, w = rgb.shape[:2]; out = np.zeros((h * 4, w * 4, 3), np.uint8)
    x = torch.from_numpy(rgb).float().div(255).permute(2, 0, 1)[None]
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            ya, yb, xa, xb = max(y0 - pad, 0), min(y0 + tile + pad, h), max(x0 - pad, 0), min(x0 + tile + pad, w)
            o = model(x[:, :, ya:yb, xa:xb]).clamp(0, 1)[0].permute(1, 2, 0).mul(255).round().byte().numpy()
            ty, tx = (y0 - ya) * 4, (x0 - xa) * 4; hh, ww = (min(y0 + tile, h) - y0) * 4, (min(x0 + tile, w) - x0) * 4
            out[y0 * 4:y0 * 4 + hh, x0 * 4:x0 * 4 + ww] = o[ty:ty + hh, tx:tx + ww]
    return out
