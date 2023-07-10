## Pytorch flags 实现调研

### 实现文件

- `c10/util/Flags.h`
- `c10/util/flags_use_gflags.cpp`
- `c10/util/flags_use_no_gflags.cpp`

### 实现细节

- Pytorch 有一个编译选项 `USE_GFLAGS` 控制是否使用基于 `gflags` 库实现的 `Flags` 功能

- `set(C10_USE_GFLAGS ${USE_GFLAGS})`

- 实现文件中会根据 `C10_USE_GFLAGS ` 使用不同的代码

- 使用 `gflags` 的实现

  就是对 `gflags` 库中的 `(DEFINE|DECLARE)_<type>` 和一些函数接口做了一层包装

### 不使用 `gflags` 的实现

#### c10/util/Flags.h

```C++
class C10_API C10FlagParser {
 public:
  bool success() {
    return success_;
  }

 protected:
  template <typename T>
  bool Parse(const std::string& content, T* value);
  bool success_{false};
};
```

- 定义了一个 `C10FlagParser` 类，其中 `Parse` 函数主要是将 `content` 赋值给 `&value`

```C++
C10_DECLARE_REGISTRY(C10FlagsRegistry, C10FlagParser, const std::string&);
```

- 然后为这个 `C10FlagParser` 类声明了一个注册表 `C10FlagsRegistry()`

  这个注册表的定义在 `c10/util/flags_use_no_gflags.cpp`：

  ```C++
  C10_DEFINE_REGISTRY(C10FlagsRegistry, C10FlagParser, const string&);
  ```

  `C10_DEFINE_REGISTRY` 展开后：

  ```C++
  C10_EXPORT ::c10::Registry<std::string, std::unique_ptr<C10FlagParser>, const string&>*
      C10FlagsRegistry() {
      static ::c10::Registry<std::string, std::unique_ptr<C10FlagParser>, const string&>*
          registry = new ::c10::
              Registry<std::string, std::unique_ptr<C10FlagParser>, const string&>();
      return registry;
    }
  ```

  定义了获取一个全局注册表的函数 `C10FlagsRegistry`，注册表 `key` 类型为 `std::string`，然后可以通过 `key` 访问 `creater`，`creater` 是一个类型 `std::function<C10FlagParser(const string&)>` 的函数，调用 `creater` 可以创建一个 `C10FlagParser` 对象（详细代码见 `c10/util/Registry.h` `class Registry`）

  `C10_DECLARE_REGISTRY` 展开后：

  ```C++
  C10_API ::c10::Registry<std::string, std::unique_ptr<C10FlagParser>, const std::string&>*
  C10FlagsRegistry();
  typedef ::c10::Registerer<std::string,  std::unique_ptr<C10FlagParser>, const std::string&> RegistererC10FlagsRegistry;
  ```

  声明了 `C10FlagsRegistry` 函数，然后声明 `RegistererC10FlagsRegistry` 类型，`RegistererC10FlagsRegistry` 可以看成 `C10FlagsRegistry()` 注册表的注册器类型，在构造一个 `RegistererC10FlagsRegistry` 对象时，会在 `C10FlagsRegistry()` 中注册 `(key, creator, help_msg)`（详细代码见 `c10/util/Registry.h` `class Registerer`）

``` C++
#define C10_DEFINE_typed_var(type, name, default_value, help_str)       \
  C10_EXPORT type FLAGS_##name = default_value;                         \
  namespace c10 {                                                       \
  namespace {                                                           \
  class C10FlagParser_##name : public C10FlagParser {                   \
   public:                                                              \
    explicit C10FlagParser_##name(const std::string& content) {         \
      success_ = C10FlagParser::Parse<type>(content, &FLAGS_##name);    \
    }                                                                   \
  };                                                                    \
  }                                                                     \
  RegistererC10FlagsRegistry g_C10FlagsRegistry_##name(                 \
      #name,                                                            \
      C10FlagsRegistry(),                                               \
      RegistererC10FlagsRegistry::DefaultCreator<C10FlagParser_##name>, \
      "(" #type ", default " #default_value ") " help_str);             \
  }

#define C10_DECLARE_typed_var(type, name) C10_API extern type FLAGS_##name
```

- `C10_DEFINE_typed_var(type, name, default_value, help_str)` 是 Pytorch 中 `DEFINE_<type>` 的下层实现
- `C10_EXPORT type FLAGS_##name = default_value;`: 定义了全局标志变量，初始化为默认值，这里使用了 `C10_EXPORT `：`#define C10_EXPORT __attribute__((__visibility__("default")))`
- 然后定义了继承 `C10FlagParser` 的类 `C10FlagParser_##name`，构造函数会调用 `C10FlagParser` 的 `Parse` 函数给 `FLAGS_##name` 赋值
- 最后定义了一个注册器对象 `g_C10FlagsRegistry_##name`，相当于在注册表 `C10FlagsRegistry()` 中注册了一个 `key` 为 `name`，`creater` 为 `C10FlagParser_##name` 的默认构造函数，也就是调用 `creater` 时相当于构造一个 `C10FlagParser_##name` 对象给 `FLAGS_##name` 赋值，实际的用法应该是调用 `C10FlagsRegistry()->Create(name, content)`
- `C10_DECLARE_typed_var(type, name)` 是  Pytorch 中 `DECLARE_<type>` 的下层实现

```C++
#define C10_DEFINE_<type>(name, default_value, help_str) \
  C10_DEFINE_typed_var(<type>, name, default_value, help_str)

#define C10_DECLARE_<type>(name) C10_DECLARE_typed_var(<type>, name)
```

#### c10/util/flags_use_no_gflags.cpp

其他函数的代码都比较简单，这里主要看解析命令行标志的 `C10_EXPORT bool ParseCommandLineFlags(int* pargc, char*** pargv)`：

```C++
C10_EXPORT bool ParseCommandLineFlags(int* pargc, char*** pargv) {
  if (*pargc == 0)
    return true;
  char** argv = *pargv;
  bool success = true;
  // 省略...
  for (int i = 1; i < *pargc; ++i) {
    string arg(argv[i]);
    // 省略如果 arg 是 --help，则输出帮助信息 ...
    // 省略判断 arg 是否符合规范 ...
    string key;
    string value;
    // 省略从 arg 解析 key 和 value 的过程 ...
    
    // 查看 key 是否在 C10FlagsRegistry() 中注册了
    if (!C10FlagsRegistry()->Has(key)) {
      success = false;
      break;
    }
    // 将 value 赋值给 FLAGS_key
    std::unique_ptr<C10FlagParser> parser(
        C10FlagsRegistry()->Create(key, value));
    if (!parser->success()) {
      success = false;
      break;
    }
  }
}
```