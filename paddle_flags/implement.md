### 实现计划：

- 代码实现方式模仿 gflags
- 代码接口的使用尽量与原接口保持一致，可以减少开发完成后宏替换的成本
- 待后续新版本 flags 库开发完善，先保留目前 paddle 使用的 flags 库，计划使用宏（或者编译选项）能够在新版本 flags 库和目前使用 gflags 的库中进行切换，待新版本 flags 库稳定后在删除目前使用的 flags 库



### 设计方案：

#### Flag 定义宏和声明宏

与目前 `paddle/phi/core/flags.h` 中的接口保持一致

- 定义宏 `PHI_DEFINE_<type>`

````
#define PHI_DEFINE_<type>(name, default_value, help_string)
````

`PHI_DEFINE_<type>` 会统一调用 `PHI_DEFINE_FLAG` 实现

- 声明宏 `PHI_DECLARE_<type>`

```
#define PHI_DECLARE_<type>(name)
```

其中 `<type>` 包括 int32, uint32, int64, uint64, double, bool, string，其中 string 的实现可能需要复杂一些

#### `PHI_DEFINE_FLAG`

```C++
#define PHI_DEFINE_FLAG(type, name, default_value, help_string) \
  namespace flag_##type {                                       \
    static const type FLAGS_##name##_default = default_value;   \
    PHI_EXPORT_FLAG type FLAGS_##name = FLAGS_##name##_default; \
    /* Register FLAG */                                         \
  }                                                             \
  using flag_##type::FLAGS_##name
```

### `FlagRegistry`

FLAG 注册表的封装：

- 有一个全局单例
- 首先实现 FLAG 的注册功能，
