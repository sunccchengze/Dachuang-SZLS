// 相机位姿旁路总线（与 frameBus 同族：Canvas 内每帧写，Canvas 外的层读）
// 为什么需要：AudioField 挂在 Canvas 之外（rAF 驱动，软渲染掉帧时声音仍连续），
// 拿不到 useThree 的 camera；CameraRig 每帧把位姿推到这里即可，零 React 渲染。
import * as THREE from 'three'

const _pos = new THREE.Vector3(0, 1450, 250)
const _fwd = new THREE.Vector3(0, 0, -1)
const _up = new THREE.Vector3(0, 1, 0)

export function pushCameraState(pos: THREE.Vector3, fwd: THREE.Vector3, up: THREE.Vector3): void {
  _pos.copy(pos)
  _fwd.copy(fwd)
  _up.copy(up)
}

export function cameraPos(): THREE.Vector3 {
  return _pos
}
export function cameraFwd(): THREE.Vector3 {
  return _fwd
}
export function cameraUp(): THREE.Vector3 {
  return _up
}
