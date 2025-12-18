# 期权功能安装说明

## 安装期权功能所需的额外依赖

期权功能需要以下Python库来计算希腊字母：

```bash
pip install scipy numpy
```

这些库已经添加到 `requirements.txt` 中，所以你也可以直接：

```bash
pip install -r requirements.txt
```

## 验证安装

运行以下Python代码验证安装：

```python
import scipy
import numpy as np
from scipy.stats import norm

print("✅ scipy 版本:", scipy.__version__)
print("✅ numpy 版本:", np.__version__)
print("✅ 测试正态分布函数:", norm.cdf(0))
```

应该输出类似：
```
✅ scipy 版本: 1.11.0
✅ numpy 版本: 1.24.0
✅ 测试正态分布函数: 0.5
```

## 开始使用

安装完成后，参考：
- [OPTIONS_QUICKSTART.md](OPTIONS_QUICKSTART.md) - 快速入门
- [options_example.py](options_example.py) - 示例代码
