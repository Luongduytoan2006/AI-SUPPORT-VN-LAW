import os, json, sys

def check_dir(data_dir="data"):
    units = 0
    warn = 0
    for name in os.listdir(data_dir):
        if not name.lower().endswith(".json"):
            continue
        path = os.path.join(data_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for art, obj in data.items():
            if "tiêu_đề" not in obj:
                raise AssertionError(f"Thiếu tiêu_đề: {name} Điều {art}")

            ok = False
            if isinstance(obj.get("khoản"), dict) and obj["khoản"]:
                for k, v in obj["khoản"].items():
                    if isinstance(v, dict) and isinstance(v.get("điểm"), dict) and v["điểm"]:
                        units += len(v["điểm"])
                    else:
                        units += 1
                ok = True
            elif isinstance(obj.get("điểm"), dict) and obj["điểm"]:
                units += len(obj["điểm"])
                ok = True
            elif isinstance(obj.get("toàn_văn"), str) and obj["toàn_văn"].strip():
                units += 1
                ok = True

            if not ok:
                warn += 1
                print(f"⚠️  BỎ QUA: {name} Điều {art} thiếu 'khoản'/'điểm'/'toàn_văn'")

    print(f"OK. Tổng đơn vị (điều/khoản/điểm): {units}. Cảnh báo: {warn}")

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    check_dir(data_dir)
