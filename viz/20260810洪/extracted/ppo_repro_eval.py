# -*- coding: utf-8 -*-
"""PPO 功率跟踪 · 忠实复现评测脚本 (2026-08-10 审计重建)。

对 model/ppo_tracking_v3_seed42.pt 进行多工况自动化测试：
  - 200 个独立随机测试 episode（固定测试种子 1000）；
  - 测算：稳态功率跟踪 MAE%（后 50% 步，排除初始调整偏航瞬态）；
  - 测算：平均调节时间（进入并稳定在 ±1.5% target 误差带内的最早秒数，dt=0.1s）；
  - 测算：稳态动作平滑度 mean|delta_yaw| (deg/step)。
结果输出至 metrics_repro.json，为前端与答辩口径提供闭环实证依据。
"""
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).parent
MODEL_PATH = HERE / "model" / "ppo_tracking_v3_seed42.pt"
OUT_PATH = HERE / "metrics_repro.json"

U_LO, U_HI = 6.0, 12.0
RHO, R_AREA, CP = 1.225, np.pi * 63.0**2, 0.45
DT = 0.1
HORIZON = 200
YAW_LIM = 30.0
A_LIM = 5.0
TARGET_LO, TARGET_HI = 0.78, 0.98
OBS_SCALE = np.array([10.0, 30.0, 5000.0, 5000.0])


def p_base_of(u):
    return 0.5 * RHO * R_AREA * CP * u**3 / 1000.0


class ActorCritic(nn.Module):
    def __init__(self):
        super().__init__()
        trunk = lambda: nn.Sequential(nn.Linear(4, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh())
        self.pi = nn.Sequential(trunk(), nn.Linear(64, 1))
        self.v = nn.Sequential(trunk(), nn.Linear(64, 1))
        self.log_std = nn.Parameter(torch.full((1,), float(np.log(1.5))))

    def act_deterministic(self, obs):
        with torch.no_grad():
            t_obs = torch.tensor(obs, dtype=torch.float32)
            mean = self.pi(t_obs).squeeze(-1)
            return np.clip(mean.numpy(), -A_LIM, A_LIM)


def evaluate(n_episodes=200, seed=1000):
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"未找到权重文件：{MODEL_PATH}")

    ckpt = torch.load(MODEL_PATH, map_location="cpu")
    net = ActorCritic()
    net.load_state_dict(ckpt["state_dict"])
    net.eval()

    rng = np.random.default_rng(seed)
    u_list = rng.uniform(U_LO, U_HI, n_episodes)
    ratio_list = rng.uniform(TARGET_LO, TARGET_HI, n_episodes)

    steady_mae_pct_list = []
    steady_mae_kw_list = []
    settle_time_list = []
    action_rate_list = []

    for idx in range(n_episodes):
        u = u_list[idx]
        p_base = p_base_of(u)
        target = ratio_list[idx] * p_base
        yaw = 0.0

        p_history = []
        a_history = []
        for step in range(HORIZON):
            p = p_base * np.cos(np.radians(yaw)) ** 1.88
            obs_raw = np.array([u, yaw, p, target])
            obs = obs_raw / OBS_SCALE
            a = float(net.act_deterministic(obs))
            yaw = np.clip(yaw + a, -YAW_LIM, YAW_LIM)
            p_history.append(p)
            a_history.append(a)

        p_arr = np.array(p_history)
        a_arr = np.array(a_history)

        # 1. 稳态 MAE（后 50% 步，即 steps 100..200）
        err_steady_kw = np.abs(p_arr[100:] - target)
        steady_mae_kw = float(err_steady_kw.mean())
        steady_mae_pct = float((err_steady_kw / target).mean() * 100.0)
        steady_mae_kw_list.append(steady_mae_kw)
        steady_mae_pct_list.append(steady_mae_pct)

        # 2. 调节时间（进入 ±1.5% 带且不再跃出的最早时间）
        rel_err = np.abs(p_arr - target) / target
        within_band = rel_err <= 0.015
        t_settle = HORIZON * DT
        for step in range(HORIZON):
            if within_band[step:].all():
                t_settle = step * DT
                break
        settle_time_list.append(t_settle)

        # 3. 动作变化平滑度
        action_rate_list.append(float(np.abs(a_arr[100:]).mean()))

    res = {
        "n_episodes": n_episodes,
        "seed": seed,
        "metrics": {
            "steady_state_mae_pct": round(float(np.mean(steady_mae_pct_list)), 3),
            "steady_state_mae_kw": round(float(np.mean(steady_mae_kw_list)), 2),
            "settling_time_mean_s": round(float(np.mean(settle_time_list)), 3),
            "settling_time_p95_s": round(float(np.percentile(settle_time_list, 95)), 3),
            "steady_action_rate_deg_per_step": round(float(np.mean(action_rate_list)), 4),
        },
        "model_file": str(MODEL_PATH.name),
        "audit_note": "2026-08-10 物理可达域靶向功率跟踪（cos^1.88 理论模型下的独立强化学习闭环验证）",
    }

    OUT_PATH.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print("=== PPO 功率跟踪 · 评测报告 ===")
    print(f"评测回合数       : {res['n_episodes']}")
    print(f"稳态跟踪 MAE(%)  : {res['metrics']['steady_state_mae_pct']:.3f} %")
    print(f"稳态跟踪 MAE(kW) : {res['metrics']['steady_state_mae_kw']:.2f} kW")
    print(f"平均调节时间 (s) : {res['metrics']['settling_time_mean_s']:.3f} s")
    print(f"95分位调节时间(s): {res['metrics']['settling_time_p95_s']:.3f} s")
    print(f"稳态平均动作抖动 : {res['metrics']['steady_action_rate_deg_per_step']:.4f} °/step")
    print(f"报告已保存至     : {OUT_PATH}")
    return res


if __name__ == "__main__":
    evaluate()
