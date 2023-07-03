### gflags 简介

ref: https://gflags.github.io/gflags/

gflags 是一个命令行标志库，用于解析命令行参数，旨在提供一种方便的方式来定义、解析和访问命令行参，可以定义各种类型的命令行标志，包括布尔值、整数、浮点数、字符串等。

#### 使用示例

``` C++
#include <gflags/gflags.h>
#include <iostream>

DEFINE_string(name, "John", "The name to greet");

int main(int argc, char* argv[]) {
  gflags::ParseCommandLineFlags(&argc, &argv, true);
  std::cout << "Hello, " << FLAGS_name << "!" << std::endl;
  return 0;
}
```

在上面的示例中，我们使用`DEFINE_string`宏定义了一个名为`name`的命令行参数，其默认值为"John"，并提供了一个描述。然后，我们使用`gflags::ParseCommandLineFlags`函数解析命令行参数，并通过`FLAGS_name`访问该参数的值。

当你在命令行中运行这个程序时，可以通过`--name`选项指定`name`参数的值：

```bash
./myprogram --name=Alice
```

#### 常用接口

1. `DEFINE_<type>(name, default_value, help)` 和 `DECLARE_<type>(name)`

   - `<type>` 可以是`bool`、`int32`、`int64`、`uint64`、`double`、`string`等
   - `DEFINE_<type>` 在全局命名空间中定义一个命令行标志，包括它的默认值和帮助信息。
   - `DECLARE_<type>` 声明一个命令行标志，这个用法相当于 `extern <type> FLAGS_name` 
   - 在一个源文件 `DECLARE` 另一个源文件 `DEFINE` 的 `FLAGS` 时，这两个文件就存在了依赖关系，官方建议将 `DECLARE` 放在对应的头文件中，如果其他源文件需要使用直接 `include` 头文件，但我觉得直接 `DECLARE` 更直观一点

2. `DEFINE_validator(name, type, function)` 和 `DECLARE_validator(name, type, function)`

   - `DEFINE_validator` 用于注册标志的验证器函数，`name`是参数的名称，`type`是参数的类型，`function`是绑定的验证函数，验证函数应该具有以下签名：`bool Validator(const T& value)`，其中`T`是参数的类型。

   - 在从命令行解析标志后，每当通过调用 `SetCommandLineOption()` 更改其值时，都会使用新值作为参数来调用验证器函数。验证函数应返回`true`表示参数值有效，返回`false`表示参数值无效，那么 `ParseCommandLineFlags` 将失效。

   - 使用示例：

     ```C++
     static bool ValidatePort(const char* flagname, int32 value) {
        if (value > 0 && value < 32768)   // value is ok
          return true;
        printf("Invalid value for --%s: %d\n", flagname, (int)value);
        return false;
     }
     DEFINE_int32(port, 0, "What port to listen on");
     DEFINE_validator(port, &ValidatePort);
     ```

3. ` gflags::ParseCommandLineFlags(&argc, &argv, true)`

   - 这个函数告诉可执行文件处理命令行标志，并根据命令行上看到的内容将 `FLAGS_*` 变量设置为适当的非默认值。

   - 这个函数调用通常位于 `main()` 开头，`argc` 和 `argv` 与传递给 `main()` 的完全相同。

   - 最后一个参数称为 `remove_flags`。如果为 true，则 `ParseCommandLineFlags` 将从 `argv` 中删除标志及其参数，并相应地修改 `argc`。在这种情况下，在函数调用之后，`argv` 将仅保存命令行参数，而不保存命令行标志。

   - 在主函数运行这个函数后可以在命令行上指定标志变量的值，如：

     ```bash
      app_containing_foo --nobig_menu --languages="chinese,japanese,korean" ...
     ```

     注意 `bool` 类型的标志可以用 `--<name>` 表示设置为 `true`，用 `--no<name>`表示 `false`，也可以使用 `--<name>=true/false`

### gflags API

- gflags.h

`#include "gflags/gflags_declare.h"`

`namespace GFLAGS_NAMESPACE {`

1. <macro> `RegisterFlagValidator`，为一个 FLAG 注册验证器
2. <macro> `DEFINE_validator`，对 `RegisterFlagValidator` 进行了一层包装
3. <struct> `CommandLineFlagInfo`，用于存放单个命令行标志的信息结构体
4. <func> `void GetAllFlags(std::vector<CommandLineFlagInfo>* OUTPUT)`
5. <func> `void ShowUsageWithFlags(const char *argv0)`
6. <func> `void ShowUsageWithFlagsRestrict(const char *argv0, const char *restrict)`
7. <func> `std::string DescribeOneFlag(const CommandLineFlagInfo& flag)`
8. <func> `void SetArgv(int argc, const char** argv)`
9. <func> `const std::vector<std::string>& GetArgvs()`
10. <func> `const char* GetArgv()`
11. <func> `const char* GetArgv0()`
12. <func> `uint32 GetArgvSum()`
13. <func> `const char* ProgramInvocationName()`
14. <func> `const char* ProgramInvocationShortName()`
15. <func> `const char* ProgramUsage()`
16. <func> `const char* VersionString()`
17. <func> `bool GetCommandLineOption(const char* name, std::string* OUTPUT)`
18. <func> `bool GetCommandLineFlagInfo(const char* name, CommandLineFlagInfo* OUTPUT)`
19. <func> `CommandLineFlagInfo GetCommandLineFlagInfoOrDie(const char* name)`
20. <enum> `FlagSettingMode`
21. <func> `std::string SetCommandLineOption (const char* name, const char* value)`
22. <func> `std::string SetCommandLineOptionWithMode(const char*, const char*, FlagSettingMode)`
23. <class> `FlagSaver`
24. <func> `std::string CommandlineFlagsIntoString()`
25. <func> `bool ReadFlagsFromString(const std::string, const char*, bool)`
26. <func> `bool AppendFlagsIntoFile(const std::string& filename, const char* prog_name)`
27. <func> `bool ReadFromFlagsFile(const std::string, const char*, bool)`
28. <func> `<Type>FromEnv(const char *varname, <type> defval)` 
29. <func> `void SetUsageMessage(const std::string& usage)`
30. <func> `void SetVersionString(const std::string& version)`
31. <func> `uint32 ParseCommandLineFlags(int *argc, char*** argv, bool remove_flags)`
32. <func> `uint32 ParseCommandLineNonHelpFlags(int *argc, char*** argv, bool remove_flags)`
33. <func> `void HandleCommandLineHelpFlags()`
34. <func> `void AllowCommandLineReparsing()`
35. <func> `void ReparseCommandLineNonHelpFlags()`
36. <func> `void ShutDownCommandLineFlags()`
37. <class> `FlagRegisterer`
38. <macro> `GFLAGS_DECLARE_FLAG_REGISTERER_CTOR`
39. <data> `const char kStrippedFlagHelp[]`

`} // namespace GFLAGS_NAMESPACE`

40. <macro> `MAYBE_STRIPPED_HELP`
41. <macro> `DEFINE_VARIABLE(type, shorttype, name, value, help)`
42. <func> `fLB::IsBoolFlag`
43. <macro> `DEFINE_<type>(name, val, txt)`，<type> 有 bool, int32, uint32, int64, uint64, double
44. <func> `fLS::dont_pass0toDEFINE_string`
45. <class> `flS::StringFlagDestructor`
46. <macro> `DEFINE_string(name, val, txt)`

`#include "gflags_gflags.h"`

- gflags_gflags.h

这个头文件把 `gflags.h` 中 `namespace GFLAGS_NAMESPACE` 中的接口放在了 `namespcae gflags` 下

- gflags_declare.h

`#define GFLAGS_NAMESPACE google`：所以 `gflags.h` 中 `namespace GFLAGS_NAMESPACE` 是 `google`

47. `namespace GFLAGS_NAMESPACE { int32, uint32, int64, uint64 }`
48. <macro> `DECLARE_VARIABLE(type, shorttype, name)`
49. <macro>  `DECLARE_<type>(name)`, <type> 包括 bool, int32, uint32, int64, uint64, double, string.

### gflags 源码实现

从 `DEFINE_<type>(name, val, txt)` 开始，除了 bool 和 string，其他类型都是直接调用 `DEFINE_VARIABLE`

```C++
#define DEFINE_int32(name, val, txt) \
   DEFINE_VARIABLE(GFLAGS_NAMESPACE::int32, I, \
                   name, val, txt)
#define DEFINE_uint32(name,val, txt) \
   DEFINE_VARIABLE(GFLAGS_NAMESPACE::uint32, U, \
                   name, val, txt)
#define DEFINE_int64(name, val, txt) \
   DEFINE_VARIABLE(GFLAGS_NAMESPACE::int64, I64, \
                   name, val, txt)
#define DEFINE_uint64(name,val, txt) \
   DEFINE_VARIABLE(GFLAGS_NAMESPACE::uint64, U64, \
                   name, val, txt)
#define DEFINE_double(name, val, txt) \
   DEFINE_VARIABLE(double, D, name, val, txt)
```

#### `DEFINE_VARIABLE` 实现

```C++
#define DEFINE_VARIABLE(type, shorttype, name, value, help)             \
  namespace fL##shorttype {                                             \
    static const type FLAGS_nono##name = value;                         \
    /* We always want to export defined variables, dll or no */         \
    GFLAGS_DLL_DEFINE_FLAG type FLAGS_##name = FLAGS_nono##name;        \
    static type FLAGS_no##name = FLAGS_nono##name;                      \
    static GFLAGS_NAMESPACE::FlagRegisterer o_##name(                   \
      #name, MAYBE_STRIPPED_HELP(help), __FILE__,                       \
      &FLAGS_##name, &FLAGS_no##name);                                  \
  }                                                                     \
  using fL##shorttype::FLAGS_##name
```

- 定义 3 个变量的解释是：每个标志有两个与之关联的变量：一个是当前值 `FLAGS_##name`，一个是默认值 `FLAGS_no##name`，然后 gflags 还定义第三个静态常量 `FLAGS_nono##name` ，这样当 `value` 是一个编译时常量时，能够确保 `FLAGS_##name` 在静态初始化阶段（程序启动前）进行初始化，而不是在全局构造阶段（程序启动后，但在 `main` 函数之前）
- `FLAGS_nono##name` 还有一个作用是：因为默认值的变量是 `FLAGS_no##name`，如果有人在 `<name>` 标志的情况下尝试定义一个 `no<name>` 标志的话，会导致编译报错，因为 bool 类型标志可以在命令行使用 `--no<name>` 设置 `FLAGS_name`  为 `false` ，这样可以避免混淆
- 然后定义了一个静态 `FlagRegisterer` 对象，后续深入了解 `FlagRegisterer` 
- 代码还将标志放置在自己的命名空间中。这个命名空间的名称是有意保持不透明的，这样做的目的是，`DEFINE` 将标志放置在奇怪的命名空间中，而 `DECLARE` 将标志从那个命名空间导入到当前命名空间中。这样做的结果是，强制要求人们使用 `DECLARE` 来访问标志，而不是直接写类似 `extern GFLAGS_DLL_DECL bool FLAGS_whatever;` 这样的代码，这样做是为了可以在DECLARE中添加额外的功能（如检查），并确保它在所有地方都能生效。

关于标志初始化的补充说明：

> 当涉及到全局变量和静态变量时，初始化的重要性在于确保它们的值在程序运行之前正确地设置。这对于命令行标志尤其重要，因为它们的值通常在程序的早期阶段就需要被读取和使用。
>
> 全局变量和静态变量在程序启动时会进行初始化。全局变量的初始化发生在全局构造阶段，而静态变量的初始化可以分为静态初始化和动态初始化两个阶段。
>
> 静态初始化是在程序启动之前进行的，它发生在全局构造函数之前。在这个阶段，编译器会将静态变量的初始值硬编码到可执行文件的数据段中。这意味着在程序启动时，这些变量已经具有正确的初始值。
>
> 动态初始化是在全局构造函数阶段进行的，它发生在程序启动后但在`main`函数执行之前。在这个阶段，编译器会执行初始化代码，将静态变量的初始值赋给它们。这种初始化方式可能会受到全局构造函数的调用顺序和其他因素的影响。
>
> 对于命令行标志来说，它们的初始值通常需要在程序的早期阶段就被读取和使用，比如在全局构造函数中。如果标志的初始值无法在静态初始化阶段设置正确，那么在全局构造阶段访问它们可能会导致不可预测的行为。这可能会影响程序的正确性和可靠性。
>
> 为了解决这个问题，上述代码使用了一个常量来初始化标志的初始值。通过将初始值定义为一个常量，它的值在编译时就可以确定并保持不变。这意味着在静态初始化阶段，编译器可以直接使用这个常量值来初始化标志，而无需等到程序运行时才进行初始化。这样做可以确保在程序开始执行之前，命令行标志的初始值已经正确地初始化。

##### `FlagRegisterer`

```C++
class GFLAGS_DLL_DECL FlagRegisterer {
 public:
  // We instantiate this template ctor for all supported types,
  // so it is possible to place implementation of the FlagRegisterer ctor in
  // .cc file.
  // Calling this constructor with unsupported type will produce linker error.
  template <typename FlagType>
  FlagRegisterer(const char* name,
                 const char* help, const char* filename,
                 FlagType* current_storage, FlagType* defvalue_storage);
};

template <typename FlagType>
FlagRegisterer::FlagRegisterer(const char* name,
                               const char* help,
                               const char* filename,
                               FlagType* current_storage,
                               FlagType* defvalue_storage) {
  FlagValue* const current = new FlagValue(current_storage, false);
  FlagValue* const defvalue = new FlagValue(defvalue_storage, false);
  RegisterCommandLineFlag(name, help, filename, current, defvalue);
}

// Force compiler to generate code for the given template specialization.
#define INSTANTIATE_FLAG_REGISTERER_CTOR(type)                  \
  template GFLAGS_DLL_DECL FlagRegisterer::FlagRegisterer(      \
      const char* name, const char* help, const char* filename, \
      type* current_storage, type* defvalue_storage)

// Do this for all supported flag types.
INSTANTIATE_FLAG_REGISTERER_CTOR(bool);
INSTANTIATE_FLAG_REGISTERER_CTOR(int32);
INSTANTIATE_FLAG_REGISTERER_CTOR(uint32);
INSTANTIATE_FLAG_REGISTERER_CTOR(int64);
INSTANTIATE_FLAG_REGISTERER_CTOR(uint64);
INSTANTIATE_FLAG_REGISTERER_CTOR(double);
INSTANTIATE_FLAG_REGISTERER_CTOR(std::string);

#undef INSTANTIATE_FLAG_REGISTERER_CTOR
```

```C++
void RegisterCommandLineFlag(const char* name,
                             const char* help,
                             const char* filename,
                             FlagValue* current,
                             FlagValue* defvalue) {
  if (help == NULL)
    help = "";
  // Importantly, flag_ will never be deleted, so storage is always good.
  CommandLineFlag* flag =
      new CommandLineFlag(name, help, filename, current, defvalue);
  FlagRegistry::GlobalRegistry()->RegisterFlag(flag);  // default registry
}
```

`DEFINE_VARIABLE` 会定义一个静态 `FlagRegisterer` 对象，然后 `FlagRegisterer` 的构造函数就是根据输入的信息在一个全局标志注册表 `FlagRegistry::GlobalRegistry()` 中注册一个 Flag

相关数据结构：

- `FlagValue`：最底层的数据结构，只保存和管理 Flag 的 value
- `CommandLineFlag`：Flag 数据结构，能够表示一个完整的 Flag
- `FlagRegistry`：Flag 注册表，有一个全局单例，用于 Flag 的注册和管理

##### `FlagValue`

```C++
class FlagValue {
 public:
  enum ValueType {
    FV_BOOL = 0,
    FV_INT32 = 1,
    FV_UINT32 = 2,
    FV_INT64 = 3,
    FV_UINT64 = 4,
    FV_DOUBLE = 5,
    FV_STRING = 6,
    FV_MAX_INDEX = 6,
  };

  template <typename FlagType>
  FlagValue(FlagType* valbuf, bool transfer_ownership_of_value);
  ~FlagValue();

  bool ParseFrom(const char* spec);
  string ToString() const;

  ValueType Type() const { return static_cast<ValueType>(type_); }

 private:
  friend class CommandLineFlag;  // for many things, including Validate()
  friend class GFLAGS_NAMESPACE::FlagSaverImpl;  // calls New()
  friend class FlagRegistry;     // checks value_buffer_ for flags_by_ptr_ map
  template <typename T> friend T GetFromEnv(const char*, T);
  friend bool TryParseLocked(const CommandLineFlag*, FlagValue*,
                             const char*, string*);  // for New(), CopyFrom()

  template <typename FlagType>
  struct FlagValueTraits;

  const char* TypeName() const;
  bool Equal(const FlagValue& x) const;
  FlagValue* New() const;   // creates a new one with default value
  void CopyFrom(const FlagValue& x);

  // Calls the given validate-fn on value_buffer_, and returns
  // whatever it returns.  But first casts validate_fn_proto to a
  // function that takes our value as an argument (eg void
  // (*validate_fn)(bool) for a bool flag).
  bool Validate(const char* flagname, ValidateFnProto validate_fn_proto) const;

  void* const value_buffer_;          // points to the buffer holding our data
  const int8 type_;                   // how to interpret value_
  const bool owns_value_;             // whether to free value on destruct

  FlagValue(const FlagValue&);   // no copying!
  void operator=(const FlagValue&);
};
```

- 成员变量：数字指针 `value_buffer_` ，数据类型 `type_`，数据是否被释放 `owns_value_`
- `bool FlagValue::ParseFrom(const char* spec)`：解析 value 字符串，给 `*value_buffer_` 赋值

##### `CommandLineFlag`

```C++
class CommandLineFlag {
 public:
  // Note: we take over memory-ownership of current_val and default_val.
  CommandLineFlag(const char* name, const char* help, const char* filename,
                  FlagValue* current_val, FlagValue* default_val);
  ~CommandLineFlag();

  const char* name() const { return name_; }
  const char* help() const { return help_; }
  const char* filename() const { return file_; }
  const char* CleanFileName() const;  // nixes irrelevant prefix such as homedir
  string current_value() const { return current_->ToString(); }
  string default_value() const { return defvalue_->ToString(); }
  const char* type_name() const { return defvalue_->TypeName(); }
  ValidateFnProto validate_function() const { return validate_fn_proto_; }
  const void* flag_ptr() const { return current_->value_buffer_; }

  FlagValue::ValueType Type() const { return defvalue_->Type(); }

  void FillCommandLineFlagInfo(struct CommandLineFlagInfo* result);

  // If validate_fn_proto_ is non-NULL, calls it on value, returns result.
  bool Validate(const FlagValue& value) const;
  bool ValidateCurrent() const { return Validate(*current_); }
  bool Modified() const { return modified_; }

 private:
  // for SetFlagLocked() and setting flags_by_ptr_
  friend class FlagRegistry;
  friend class GFLAGS_NAMESPACE::FlagSaverImpl;  // for cloning the values
  // set validate_fn
  friend bool AddFlagValidator(const void*, ValidateFnProto);

  // This copies all the non-const members: modified, processed, defvalue, etc.
  void CopyFrom(const CommandLineFlag& src);

  void UpdateModifiedBit();

  const char* const name_;     // Flag name
  const char* const help_;     // Help message
  const char* const file_;     // Which file did this come from?
  bool modified_;              // Set after default assignment?
  FlagValue* defvalue_;        // Default value for flag
  FlagValue* current_;         // Current value for flag
  // This is a casted, 'generic' version of validate_fn, which actually
  // takes a flag-value as an arg (void (*validate_fn)(bool), say).
  // When we pass this to current_->Validate(), it will cast it back to
  // the proper type.  This may be NULL to mean we have no validate_fn.
  ValidateFnProto validate_fn_proto_;

  CommandLineFlag(const CommandLineFlag&);   // no copying!
  void operator=(const CommandLineFlag&);
};
```

##### `FlagRegistry`

```C++
class FlagRegistry {
 public:
  FlagRegistry() {
  }
  ~FlagRegistry() {
    // Not using STLDeleteElements as that resides in util and this
    // class is base.
    for (FlagMap::iterator p = flags_.begin(), e = flags_.end(); p != e; ++p) {
      CommandLineFlag* flag = p->second;
      delete flag;
    }
  }

  static void DeleteGlobalRegistry() {
    delete global_registry_;
    global_registry_ = NULL;
  }

  // Store a flag in this registry.  Takes ownership of the given pointer.
  void RegisterFlag(CommandLineFlag* flag);

  void Lock() { lock_.Lock(); }
  void Unlock() { lock_.Unlock(); }

  // Returns the flag object for the specified name, or NULL if not found.
  CommandLineFlag* FindFlagLocked(const char* name);

  // Returns the flag object whose current-value is stored at flag_ptr.
  // That is, for whom current_->value_buffer_ == flag_ptr
  CommandLineFlag* FindFlagViaPtrLocked(const void* flag_ptr);

  // A fancier form of FindFlag that works correctly if name is of the
  // form flag=value.  In that case, we set key to point to flag, and
  // modify v to point to the value (if present), and return the flag
  // with the given name.  If the flag does not exist, returns NULL
  // and sets error_message.
  CommandLineFlag* SplitArgumentLocked(const char* argument,
                                       string* key, const char** v,
                                       string* error_message);

  // Set the value of a flag.  If the flag was successfully set to
  // value, set msg to indicate the new flag-value, and return true.
  // Otherwise, set msg to indicate the error, leave flag unchanged,
  // and return false.  msg can be NULL.
  bool SetFlagLocked(CommandLineFlag* flag, const char* value,
                     FlagSettingMode set_mode, string* msg);

  static FlagRegistry* GlobalRegistry();   // returns a singleton registry

 private:
  friend class GFLAGS_NAMESPACE::FlagSaverImpl;  // reads all the flags in order to copy them
  friend class CommandLineFlagParser;    // for ValidateUnmodifiedFlags
  friend void GFLAGS_NAMESPACE::GetAllFlags(vector<CommandLineFlagInfo>*);

  // The map from name to flag, for FindFlagLocked().
  typedef map<const char*, CommandLineFlag*, StringCmp> FlagMap;
  typedef FlagMap::iterator FlagIterator;
  typedef FlagMap::const_iterator FlagConstIterator;
  FlagMap flags_;

  // The map from current-value pointer to flag, fo FindFlagViaPtrLocked().
  typedef map<const void*, CommandLineFlag*> FlagPtrMap;
  FlagPtrMap flags_by_ptr_;

  static FlagRegistry* global_registry_;   // a singleton registry

  Mutex lock_;

  static void InitGlobalRegistry();

  // Disallow
  FlagRegistry(const FlagRegistry&);
  FlagRegistry& operator=(const FlagRegistry&);
};
```

- `FlagRegistry`是一个标志注册表的类，用于存储和管理所有的标志对象，是一个单例类，只有一个全局实例。

成员变量：

- `FlagMap flags_`：Flag 名称到 `CommandLineFlag*` 的映射
- `FlagPtrMap flags_by_ptr_`：Flag value 指针到 `CommandLineFlag*` 的映射
- `static FlagRegistry* global_registry_;`：全局单例

成员函数：

- `void RegisterFlag(CommandLineFlag* flag)`：注册标志
- `CommandLineFlag* FindFlagLocked(const char* name)`：通过名称查找标志
- `CommandLineFlag* FindFlagViaPtrLocked(const void* flag_ptr)`：通过 value 指针查找标志
- `SplitArgumentLocked(const char* argument, string* key, const char** v, string* error_message)`：根据参数的形式解析标志名称和值。如果参数的形式是 `flag=value`，则将标志名称存储在 `key` 中，将值存储在 `v` 中，并返回与给定名称匹配的标志对象的指针。如果找不到匹配的标志对象，返回`NULL`，并设置`error_message`
- `SetFlagLocked(CommandLineFlag* flag, const char* value, FlagSettingMode set_mode, string* msg)`：设置标志的值。根据给定的标志对象、值和设置模式，将标志的值设置为指定的值。如果成功设置标志的值，将在 `msg` 中指示新的标志值，并返回 `true`，否则，将在`msg`中指示错误，保持标志不变，并返回`false`。
- `GlobalRegistry()`：返回全局注册表对象的单例

#### `ParseCommandLineFlags` 实现

```C++
static uint32 ParseCommandLineFlagsInternal(int* argc, char*** argv,
                                            bool remove_flags, bool do_report) {
  SetArgv(*argc, const_cast<const char**>(*argv));    // save it for later

  FlagRegistry* const registry = FlagRegistry::GlobalRegistry();
  CommandLineFlagParser parser(registry);

  // When we parse the commandline flags, we'll handle --flagfile,
  // --tryfromenv, etc. as we see them (since flag-evaluation order
  // may be important).  But sometimes apps set FLAGS_tryfromenv/etc.
  // manually before calling ParseCommandLineFlags.  We want to evaluate
  // those too, as if they were the first flags on the commandline.
  registry->Lock();
  parser.ProcessFlagfileLocked(FLAGS_flagfile, SET_FLAGS_VALUE);
  // Last arg here indicates whether flag-not-found is a fatal error or not
  parser.ProcessFromenvLocked(FLAGS_fromenv, SET_FLAGS_VALUE, true);
  parser.ProcessFromenvLocked(FLAGS_tryfromenv, SET_FLAGS_VALUE, false);
  registry->Unlock();

  // Now get the flags specified on the commandline
  const int r = parser.ParseNewCommandLineFlags(argc, argv, remove_flags);

  if (do_report)
    HandleCommandLineHelpFlags();   // may cause us to exit on --help, etc.

  // See if any of the unset flags fail their validation checks
  parser.ValidateUnmodifiedFlags();

  if (parser.ReportErrors())        // may cause us to exit on illegal flags
    gflags_exitfunc(1);
  return r;
}

uint32 ParseCommandLineFlags(int* argc, char*** argv, bool remove_flags) {
  return ParseCommandLineFlagsInternal(argc, argv, remove_flags, true);
}
```

- `SetArgv(*argc, const_cast<const char**>(*argv))`：对命令行输入进行一些预处理，会保存在一些全局变量中
- `CommandLineFlagParser parser(registry)`：主要相关的一个数据结构，通过 FlagRegistry 的全局单例构造
- 处理一些特殊的标志参数，预先定义为空，如`FLAGS_flagfile`、`FLAGS_fromenv` 和 `FLAGS_tryfromenv`
- `parser.ParseNewCommandLineFlags(argc, argv, remove_flags)`：解析命令行
- 后续都是一些验证和错误处理代码，暂时不细看

##### `CommandLineFlagParser`

```C++
class CommandLineFlagParser {
 public:
  // The argument is the flag-registry to register the parsed flags in
  explicit CommandLineFlagParser(FlagRegistry* reg) : registry_(reg) {}
  ~CommandLineFlagParser() {}

  // Stage 1: Every time this is called, it reads all flags in argv.
  // However, it ignores all flags that have been successfully set
  // before.  Typically this is only called once, so this 'reparsing'
  // behavior isn't important.  It can be useful when trying to
  // reparse after loading a dll, though.
  uint32 ParseNewCommandLineFlags(int* argc, char*** argv, bool remove_flags);

  // Stage 2: print reporting info and exit, if requested.
  // In gflags_reporting.cc:HandleCommandLineHelpFlags().

  // Stage 3: validate all the commandline flags that have validators
  // registered and were not set/modified by ParseNewCommandLineFlags.
  void ValidateFlags(bool all);
  void ValidateUnmodifiedFlags();

  // Stage 4: report any errors and return true if any were found.
  bool ReportErrors();

  // Set a particular command line option.  "newval" is a string
  // describing the new value that the option has been set to.  If
  // option_name does not specify a valid option name, or value is not
  // a valid value for option_name, newval is empty.  Does recursive
  // processing for --flagfile and --fromenv.  Returns the new value
  // if everything went ok, or empty-string if not.  (Actually, the
  // return-string could hold many flag/value pairs due to --flagfile.)
  // NB: Must have called registry_->Lock() before calling this function.
  string ProcessSingleOptionLocked(CommandLineFlag* flag,
                                   const char* value,
                                   FlagSettingMode set_mode);

  // Set a whole batch of command line options as specified by contentdata,
  // which is in flagfile format (and probably has been read from a flagfile).
  // Returns the new value if everything went ok, or empty-string if
  // not.  (Actually, the return-string could hold many flag/value
  // pairs due to --flagfile.)
  // NB: Must have called registry_->Lock() before calling this function.
  string ProcessOptionsFromStringLocked(const string& contentdata,
                                        FlagSettingMode set_mode);

  // These are the 'recursive' flags, defined at the top of this file.
  // Whenever we see these flags on the commandline, we must take action.
  // These are called by ProcessSingleOptionLocked and, similarly, return
  // new values if everything went ok, or the empty-string if not.
  string ProcessFlagfileLocked(const string& flagval, FlagSettingMode set_mode);
  // diff fromenv/tryfromenv
  string ProcessFromenvLocked(const string& flagval, FlagSettingMode set_mode,
                              bool errors_are_fatal);

 private:
  FlagRegistry* const registry_;
  map<string, string> error_flags_;      // map from name to error message
  // This could be a set<string>, but we reuse the map to minimize the .o size
  map<string, string> undefined_names_;  // --[flag] name was not registered
};
```

- 命令行解析分为 2 个阶段：

  第一阶段，遍历命令行参数`argv`，对于每个类似于标志的参数，解析该参数并设置对应的`FLAGS_*`变量，对于无法理解的标志参数，它会将其与解释信息一起存储在一个向量中。

  第二阶段，它处理报告类的标志选项，如`--help`和`--mpm_version`。具体的处理过程在`gflags_reporting.cc`的`HandleCommandLineHelpFlags()`函数中实现

  可选的第三阶段，打印错误信息

- `ParseNewCommandLineFlags` 是实现第一阶段的方法

- `ProcessSingleOptionLocked` 和 `ProcessOptionsFromStringLocked` 是两个下层函数

- `ProcessFlagfileLocked` 和 `ProcessFromenvLocked` 用于处理几个特殊的 'recursive' flags，主要是 `FLAGS_flagfile`，`FLAGS_fromenv`，`FLAGS_tryfromenv`，这几个 FLAG 在 `gflags.cc` 中定义了：

  ```C++
  // Special flags, type 1: the 'recursive' flags.  They set another flag's val.
  DEFINE_string(flagfile,   "", "load flags from file");
  DEFINE_string(fromenv,    "", "set flags from the environment"
                                " [use 'export FLAGS_flag1=value']");
  DEFINE_string(tryfromenv, "", "set flags from the environment if present");
  
  // Special flags, type 2: the 'parsing' flags.  They modify how we parse.
  DEFINE_string(undefok, "", "comma-separated list of flag names that it is okay to specify "
                             "on the command line even if the program does not define a flag "
                             "with that name.  IMPORTANT: flags in this list that have "
                             "arguments MUST use the flag=value format");
  ```

  - `--flagfile`：从文件中加载标志，接受一个文件路径作为值，用于指定包含要设置的标志的文件。
  - `--fromenv`：从环境变量中设置标志，接受一个环境变量名作为值，用于指定要读取的环境变量，并将其值用于设置相应的标志。
  - `--tryfromenv`：尝试从环境变量中设置标志，与`--fromenv`类似，但不会引发错误，如果环境变量不存在，则不会设置标志。
  - `--undefok`：指定在命令行中指定某些未定义的标志名是允许的，接受一个逗号分隔的标志名称列表作为值。当程序未定义某个标志但在命令行中指定了该标志名时，该标志将被视为有效。注意，该列表中的具有参数的标志必须使用`flag=value`的格式，私有成员 `undefined_names_` 与这个相关