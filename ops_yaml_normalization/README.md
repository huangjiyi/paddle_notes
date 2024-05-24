### yaml 算子梳理

在 get_consistent_ops.py 脚本中实现了对 paddle/phi/ops/yaml/inconsistent 中单独面向动态图和静态图的 op 进行了解析，解析结果为：
``` bash
Verify consistency for forward ops yaml:
ops num in dygraph_ops: 127
ops num in static_ops: 193
shared ops num: 123          # 动静态图共有的算子
dygraph unique ops num: 4    # 动态图独有
static unique ops num: 70    # 静态图独有
consistent ops num: 65       # 共有的算子中定义完全相同
inconsistent ops num: 58     # 共有的算子中定义存在区别

# 反向算子解析过程同上
Verify consistency for backward ops yaml:
ops num in dygraph_ops: 84
ops num in static_ops: 95
shared ops num: 81
dygraph unique ops num: 3
static unique ops num: 14
consistent ops num: 67
inconsistent ops num: 14

both consistent ops num: 61             # 前反向定义均完全相同的算子(前向)
both consistent ops backward num: 32    # 前反向定义均完全相同的算子(反向)
```

### 动静一致算子迁移

对于解析得到的动静一致的 61 个前向算子和对应的 32 个反向算子，需要迁移至 ops.yaml


get_consistent_ops.py 脚本实现了自动生成迁移后的 yaml 文件，然后手工把一些删掉的注释还原即可，避免了人工一个个算子迁移的繁琐

### 算子迁移后出现的问题
1. 旧 IR 算子重复定义：新 IR 下动静一致的算子迁移到 ops.yaml 后，可能在旧 IR 静态图（legacy/static_ops.yaml）中依然存在该算子的定义，并且一些算子在旧 IR 下动静并不一致，没办法直接移除，这种情况下可能会出现算子重复定义报错的问题（ops.yaml 和 legacy/static_ops.yaml 存在同一个算子的定义）
   
   Solution：在旧 IR 根据 ops.yaml 自动生成算子定义时跳过这些迁移的算子，可能其中有些算子没有问题，但为了减少排查工作量，直接对 legacy/static_ops.yaml 不进行处理，同时跳过所有迁移的算子（legacy/ops_exclude.yaml），后续旧 IR 退场直接移除 legacy 目录就可以了
2. 不同 yaml 文件算子 invoke：目前 pir 算子定义自动生成只支持 invoke 同一个 yaml 文件中的算子，但不同 yaml 文件的算子也需要被复用，比如 static_ops.yaml 复用 ops.yaml，backward.yaml 复用 ops.yaml。如果 yaml 中指定了 invoke op 但在当前 yaml 文件找不到 invoke 的 op 会导致生成的算子定义 Build 函数为空，然后在调用的时候会报错，因此需要修复。


