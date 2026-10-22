"""Интерактивный 3D-просмотрщик (HTML + three.js) для каждого варианта.

    python tools/export_viewer.py path/to/three.min.js [номер варианта ...]

Результат: out/<вариант>/viewer.html — открывается в любом браузере,
мышь: вращение (ЛКМ), сдвиг (ПКМ), масштаб (колесо).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gym.scene import Box, Cyl  # noqa: E402
from gym.variants import VARIANTS  # noqa: E402

CUT_ZONE = 400  # мм от внутренней грани «разрезаемой» стены
CUT_Z = 300


def is_front(p):
    """Элемент у южной или западной стены выше отметки разреза."""
    if isinstance(p, Box):
        x1, y1 = p.x + p.dx, p.y + p.dy
    elif isinstance(p, Cyl):
        x1, y1 = p.cx + p.r, p.cy + p.r
    else:
        x1 = p.x + (p.length if p.axis == "x" else p.r)
        y1 = p.y + (p.length if p.axis == "y" else p.r)
    return y1 <= CUT_ZONE or x1 <= CUT_ZONE


def scene_json(sc):
    out = []
    for p in sc.prims:
        t = type(p).__name__
        d = dict(p.__dict__)
        d["t"] = t
        d["ceil"] = p.item == "Перекрытие"
        front = is_front(p)
        if front:
            z0 = p.z if t != "HCyl" else p.z - p.r
            if z0 >= CUT_Z:
                d["cut"] = "hide"
            elif t == "Box" and p.z + p.dz > CUT_Z:
                d["cut"] = CUT_Z - p.z  # высота после разреза
        out.append(d)
    return dict(title=sc.title, size=sc.size, prims=out)


TEMPLATE = r"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
html,body{margin:0;height:100%;background:#eef1f4;font:14px system-ui,sans-serif;overflow:hidden}
#ui{position:absolute;left:12px;top:12px;background:#fffd;padding:10px 12px;border-radius:8px;box-shadow:0 1px 6px #0002;max-width:calc(100% - 48px)}
#ui h1{font-size:15px;margin:0 0 6px}
#ui label{display:block;margin:3px 0;cursor:pointer}
#tip{position:absolute;pointer-events:none;background:#111c;color:#fff;padding:3px 7px;border-radius:4px;display:none;font-size:13px}
canvas{display:block}
</style></head><body>
<div id="ui"><h1>__TITLE__</h1>
<label><input type="checkbox" id="cut" checked> Разрез (скрыть перекрытие и переднюю часть стен)</label>
<div style="color:#555;font-size:12px;margin-top:4px">ЛКМ — вращать, ПКМ — сдвиг, колесо — масштаб. Наведите на объект, чтобы увидеть его название.</div>
</div><div id="tip"></div>
<script>__THREE__</script>
<script>
const DATA = __DATA__;
const [L, W, H] = DATA.size;
const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeef1f4);
const camera = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 50, 400000);
camera.up.set(0, 0, 1);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 1.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(-L * 0.6, -W * 1.5, H * 4);
sun.target.position.set(L / 2, W / 2, 0);
sun.castShadow = true;
sun.shadow.mapSize.set(4096, 4096);
const sc = sun.shadow.camera; const R = Math.max(L, W);
sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = 100; sc.far = R * 8;
sun.shadow.bias = -0.0005;
scene.add(sun, sun.target);

const mats = {};
function mat(c) {
  if (!mats[c]) {
    const glass = ["#9fd3f0", "#dbeafe"].includes(c);
    mats[c] = new THREE.MeshStandardMaterial({color: c, roughness: glass ? 0.1 : 0.75,
      metalness: 0.05, transparent: glass, opacity: glass ? 0.55 : 1});
  }
  return mats[c];
}
function tube(r, rin, h) {
  const seg = r > 400 ? 96 : 32;
  if (!rin) return new THREE.CylinderGeometry(r, r, h, seg).rotateX(Math.PI / 2).translate(0, 0, h / 2);
  const s = new THREE.Shape(); s.absarc(0, 0, r, 0, Math.PI * 2, false);
  const hole = new THREE.Path(); hole.absarc(0, 0, rin, 0, Math.PI * 2, true);
  s.holes.push(hole);
  return new THREE.ExtrudeGeometry(s, {depth: h, bevelEnabled: false, curveSegments: seg});
}
const cutable = [];
for (const p of DATA.prims) {
  let g;
  if (p.t === "Box") {
    g = new THREE.BoxGeometry(p.dx, p.dy, p.dz).translate(p.x + p.dx / 2, p.y + p.dy / 2, p.z + p.dz / 2);
  } else if (p.t === "Cyl") {
    g = tube(p.r, p.r_in, p.h).translate(p.cx, p.cy, p.z);
  } else {
    g = tube(p.r, p.r_in, p.length);
    if (p.axis === "x") g.rotateY(Math.PI / 2); else g.rotateX(-Math.PI / 2);
    g.translate(p.x, p.y, p.z);
  }
  const m = new THREE.Mesh(g, mat(p.color));
  m.castShadow = true; m.receiveShadow = true;
  m.userData = p;
  scene.add(m);
  if (p.ceil || p.cut !== undefined) cutable.push(m);
  if (typeof p.cut === "number") {
    const g2 = new THREE.BoxGeometry(p.dx, p.dy, p.cut).translate(p.x + p.dx / 2, p.y + p.dy / 2, p.z + p.cut / 2);
    const m2 = new THREE.Mesh(g2, mat(p.color)); m2.userData = p; m2.receiveShadow = true;
    m2.userData.cutPart = true; m2.visible = false; scene.add(m2); m.userData.twin = m2;
  }
}
function applyCut(on) {
  for (const m of cutable) {
    m.visible = !on;
    if (m.userData.twin) m.userData.twin.visible = on;
  }
}
document.getElementById("cut").onchange = e => { applyCut(e.target.checked); draw(); };
applyCut(true);

// --- простая орбитальная камера
const target = new THREE.Vector3(L / 2, W / 2, H * 0.25);
let az = -2.2, el = 0.62, dist = Math.hypot(L, W) * 1.25;
const params = new URLSearchParams(location.search);
if (params.get("az")) az = +params.get("az");
if (params.get("el")) el = +params.get("el");
if (params.get("d")) dist *= +params.get("d");
function placeCam() {
  camera.position.set(target.x + dist * Math.cos(el) * Math.cos(az),
                      target.y + dist * Math.cos(el) * Math.sin(az),
                      target.z + dist * Math.sin(el));
  camera.lookAt(target);
}
function draw() { placeCam(); renderer.render(scene, camera); }
let drag = null;
renderer.domElement.addEventListener("pointerdown", e => { drag = {x: e.clientX, y: e.clientY, b: e.button}; renderer.domElement.setPointerCapture(e.pointerId); });
renderer.domElement.addEventListener("pointerup", () => drag = null);
renderer.domElement.addEventListener("contextmenu", e => e.preventDefault());
const ray = new THREE.Raycaster(), tip = document.getElementById("tip");
renderer.domElement.addEventListener("pointermove", e => {
  if (drag) {
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
    if (drag.b === 0 && !e.shiftKey) { az -= dx * 0.005; el = Math.max(0.05, Math.min(1.5, el + dy * 0.005)); }
    else {
      const k = dist / innerHeight;
      const right = new THREE.Vector3().subVectors(camera.position, target).cross(camera.up).normalize();
      target.addScaledVector(right, dx * k); target.z += dy * k;
    }
    draw(); return;
  }
  ray.setFromCamera({x: e.clientX / innerWidth * 2 - 1, y: -e.clientY / innerHeight * 2 + 1}, camera);
  const hit = ray.intersectObjects(scene.children.filter(o => o.isMesh && o.visible))[0];
  if (hit) { tip.style.display = "block"; tip.textContent = hit.object.userData.item;
    tip.style.left = e.clientX + 14 + "px"; tip.style.top = e.clientY + 10 + "px"; }
  else tip.style.display = "none";
});
renderer.domElement.addEventListener("wheel", e => { e.preventDefault(); dist *= Math.exp(e.deltaY * 0.001); draw(); }, {passive: false});
addEventListener("resize", () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); draw(); });
if (params.get("noui")) document.getElementById("ui").style.display = "none";
draw();
window.__ready = true;
</script></body></html>
"""


def main(three_path, nums):
    three = open(three_path, encoding="utf-8").read()
    for n in nums:
        sc = VARIANTS[n]()
        out = os.path.join(os.path.dirname(__file__), "..", "out", sc.name)
        os.makedirs(out, exist_ok=True)
        html = (TEMPLATE.replace("__TITLE__", sc.title)
                .replace("__DATA__", json.dumps(scene_json(sc), ensure_ascii=False))
                .replace("__THREE__", three))
        with open(os.path.join(out, "viewer.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print(sc.name, "->", os.path.join(out, "viewer.html"))


if __name__ == "__main__":
    main(sys.argv[1], [int(a) for a in sys.argv[2:]] or sorted(VARIANTS))
