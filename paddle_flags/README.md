## Paddle flags 机制开发

### 背景

外部用户同时使用 paddle C++ 库和 gflags 库时，会出现以下错误：

```bash
ERROR: something wrong with flag 'flagfile' in file '/Paddle/third_party/gflags/src/gflags.cc'.  One possibility: file '/Paddle/third_party/gflags/src/gflags.cc' is being linked both statically and dynamically into this executable.
```

原因：在 `gflags.cc` 中，会定义一些全局变量，比如 `FLAGS_flagfile`：

``` C++
DEFINE_string(flagfile,   "", "load flags from file");
```

因为 Paddle 依赖了 gflags，所以 `libpaddle.so` 中包含了 `FLAGS_flagfile` 这个符号，然后当用户在使用 Paddle C++ 库的同时也使用的外部的 gflags 库，就会因为符号重复定义而报错。

解决方案：开发 Paddle 自己的 flags 库

#### 调研计划

- gflags 库接口调研，Paddle 中用了哪些 gflags 接口
- Pytorch flags 库实现调研
- gflags 库源码实现

### Paddle 中用到的 gflags 用法

#### 用法统计

- 搜索 `#include "gflags/`，用 113 处用法，其中只有一处是 `#include "gflags/gflags_declare.h"`，其余全是 `#include "gflags/gflags.h"`（`gflags.h` 包含了 `gflags_declare.h`）
- 搜索 `google::[^(protobuf)]` 有一处 `google::ParseCommandLineFlags` 的用法
- 搜索 `GFLAGS_NAMESPACE::`，在 27 个文件中有 41 处用法，包括：
  1. `GFLAGS_NAMESPACE::ParseCommandLineFlags`：23 处
  2. `GFLAGS_NAMESPACE::GetCommandLineOption`：1 处
  3. `GFLAGS_NAMESPACE::SetCommandLineOption`：2 处
  4. `GFLAGS_NAMESPACE::AllowCommandLineReparsing()`：1 处
  5. `GFLAGS_NAMESPACE::<Type>FromEnv`：4 处
  6. `GFLAGS_NAMESPACE::(int32|uint32|int64|uint64)`：8 处
  7. `GFLAGS_NAMESPACE::FlagRegisterer`：2 处
- 搜索其余命名空间的用法（较少）：
  1. `fLB::CompileAssert`, `fLB::IsBoolFlag`
  2. `fLS::clstring`, `fLS::FLAGS_##name`, `fLS::StringFlagDestructor`, `fLS::dont_pass0toDEFINE_string`
- 搜索 `gflags` 中定义的宏
  1. `MAYBE_STRIPPED_HELP(`：2 处
  2. `DEFINE_VARIABLE(`：7 处
  3. `DEFINE_(bool|int32|uint32|int64|uint64|double|string)`: 202 处
  4. `DECLARE_VARIABLE`: 7 处
  5. `DECLARE_(bool|int32|uint32|int64|uint64|double|string)`: 376 处

#### 用法分析

1. `ParseCommandLineFlags`

   用于解析运行时命令行输入的标志，大部分在测试文件中使用

2. `bool GetCommandLineOption(const char* name, std::string* OUTPUT)`

   用于获取 FLAG 的值，FLAG 存在返回 true，并将 FLAGG 的值存在 OUTPUT；否则返回 false

3. `std::string SetCommandLineOption (const char* name, const char* value)`

   将 `value` 赋值给 `FLAGS_name`，并返回一个描述字符串，如果返回字符串为空表示 `FLAGS_name` 不存在，或者 `value` 不是有效的

4. `void AllowCommandLineReparsing()`

   允许命令行重新解析

5. `bool <Type>FromEnv(const char *varname, <type> defval)`

   获取环境变量 `varname` 的值，如果 `varname` 不存在，返回 `defval`

6. `(DEFINE|DECLARE)_(bool|int32|uint32|int64|uint64|double|string)`：主要被使用的 2 个接口

   `DEFINE` 用于定义目标类型的 FLAG，相当于定义一个全局变量 `FLAGS_name`

   `DECLARE` 用于声明 FLAG，相当于 `extern` 用法

7. `GFLAGS_NAMESPACE::(int32|uint32|int64|uint64)`，`FlagRegisterer`, `fLB::xxx`, `fLS:xxx`, `MAYBE_STRIPPED_HELP`, `(DEFINE|DECLARE)_VARIABLE`

   `PHI_(DEFINE|DECLARE)_<type>` 的底层实现，见 `paddle/phi/core/flags.h`，后续实现了 paddle 自己的 flags 机制可以移除