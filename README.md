# SSR2Surge

将订阅地址自动转换为surge配置信息

参考:[external-proxy-provider](https://community.nssurge.com/d/3-external-proxy-provider)

在新的 Surge Mac Build 622 中加入了一个有些复杂的新功能：External Proxy Provider，可以让 Surge 与其他代理软件更方便的协同工作。

以下以 shadowsocks-libev 为例进行说明：

首先增加了新的 Policy 类型：external，定义行为：

```
[Proxy]
External = external, exec = "/usr/local/bin/ss-local", args = "-c", args = "/usr/local/etc/shadowsocks-libev.json", local-port = 1080, addresses = 11.22.33.44
```
其中 args 和 addresses 参数为选填，其他必填。args 和 addresses 字段可以反复使用进行追加。

配置后，Surge 会进行以下工作：

1. 在使用到该策略时，使用 exec 和 args 参数启动该外部程序，之后向 SOCKS5 127.0.0.1:[local-port] 转发请求；
2. 如果外部进程被终止，当再次使用该策略时会自动进行重启；
3. Surge 会在启动 Enhanced Mode 时自动将 addresses 参数中的地址排除在 TUN 外；（所以请在该字段填写使用的代理 IP 地址）
4. 当由 Surge 启动的外部进程的请求被 TUN 处理时，永远使用 DIRECT 策略；（为了应对像 obfs-local 这样的插件请求问题，外部进程的子进程也会被同样处理）
5. Surge 退出时自动关闭所有外部进程，Enhanced Mode 关闭时自动清理加入的路由表。


一些注意事项：

1. 外部进程的 stdout 和 stderr 会被重定向到 /tmp/Surge-External-xxxxxx.log，方便进行排错；
2. 由于外部进程可能需要一点时间进行启动，所以如果访问 127.0.0.1:[local-port] 时遇到 Refused 错误，会在 500ms 后自动进行重试，每个请求最多重试 6 次；
3. 上述 3 和 4 的功能是有重叠的，请尽量使用 addresses 声明使用到的地址以排除 TUN 处理，这样可以减少系统开销，4 的功能是一重额外保护；
4. iOS 版本如果使用到了该策略，会当做 REJECT 处理。